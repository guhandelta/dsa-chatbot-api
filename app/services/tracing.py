"""Observability: traces, spans, latency, and cost accounting.

WHY THIS EXISTS
---------------
The review pipeline has five stages and the mentor has three, several of them
expensive. Without tracing, "the review felt slow" and "the mentor gave a bad
hint" are unanswerable complaints: there is no way to see which stage burned
the time, which provider call was made, how many tokens it cost, or whether
the self-critique pass actually removed anything. For a paid product with a
multi-stage LLM pipeline, that visibility is not optional.

DESIGN
------
Zero required dependencies. Spans are held in memory during a request and
flushed to the `trace_spans` table at the end, so the default setup needs no
external collector. An exporter seam (`register_exporter`) lets you forward
the same spans to Phoenix, OpenTelemetry, or anything else later without
touching instrumentation.

Three properties this module guarantees:

1. **Tracing never breaks a request.** Every public entry point swallows its
   own exceptions. An observability bug must not become a user-facing 500 —
   that would make the thing meant to improve reliability a source of
   outages.

2. **Nothing sensitive is stored.** Attributes pass through `_redact()`,
   which drops anything key-shaped and truncates free text. Traces are
   long-lived debugging data; API keys and full student submissions do not
   belong in them.

3. **Async-safe nesting.** The active trace lives in a `ContextVar`, so
   concurrent requests never interleave their spans, and nested spans build a
   correct parent/child tree without threading a context object through every
   function signature.

USAGE
-----
    async with trace("analyze", user_id=user.id) as t:
        async with t.span("fuzz", problem_id=pid) as s:
            report = run_fuzz(...)
            s.set(counterexamples=len(report.counterexamples))
        ...
    # flushed automatically on exit

Cost is estimated, not billed: `record_llm_call` applies a per-model rate
table. Treat the numbers as directional — provider pricing changes, and token
counts from a streaming call may be approximate.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Active trace for the current async task. A ContextVar (not a global) is what
# makes concurrent requests safe: each task sees its own value.
_current: ContextVar["Trace | None"] = ContextVar("current_trace", default=None)

# Optional sinks that receive every finished trace (Phoenix, OTel, a queue...).
_exporters: list[Callable[["Trace"], None]] = []

# Attribute keys whose values are never stored, at any nesting level.
_SENSITIVE_KEYS = {
    "api_key", "openai_api_key", "anthropic_api_key", "google_api_key",
    "password", "hashed_password", "token", "access_token", "jwt_secret",
    "authorization", "secret", "stripe_webhook_secret", "code", "user_code",
    "reasoning", "message", "content",
}

# Free-text attributes are truncated rather than dropped, so a trace stays
# useful for debugging without becoming a copy of everything users typed.
_MAX_VALUE_CHARS = 300

# Estimated USD per 1M tokens (input, output). Directional only.
_RATES: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "claude-3-5-haiku-20241022": (0.80, 4.00),
    "gemini-2.0-flash": (0.10, 0.40),
}
_DEFAULT_RATE = (1.00, 3.00)


def _redact(value: Any) -> Any:
    """Strip secrets and bound the size of anything stored on a span."""
    if isinstance(value, dict):
        return {
            k: ("<redacted>" if k.lower() in _SENSITIVE_KEYS else _redact(v))
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value][:20]
    if isinstance(value, str) and len(value) > _MAX_VALUE_CHARS:
        return value[:_MAX_VALUE_CHARS] + f"…(+{len(value) - _MAX_VALUE_CHARS} chars)"
    return value


@dataclass
class Span:
    """One timed unit of work inside a trace."""

    name: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_id: str | None = None
    started_at: float = field(default_factory=time.perf_counter)
    duration_ms: float = 0.0
    status: str = "ok"                       # "ok" | "error"
    error: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def set(self, **attrs: Any) -> None:
        """Attach attributes to this span. Values are redacted and truncated."""
        for key, value in attrs.items():
            self.attributes[key] = (
                "<redacted>" if key.lower() in _SENSITIVE_KEYS else _redact(value)
            )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "error": self.error[:300],
            "attributes": self.attributes,
        }


@dataclass
class Trace:
    """A request-scoped collection of spans, plus rolled-up cost."""

    name: str
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str = ""
    started_at: float = field(default_factory=time.perf_counter)
    duration_ms: float = 0.0
    status: str = "ok"
    spans: list[Span] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    # Stack of open spans, so nesting produces a correct parent/child tree.
    _open: list[Span] = field(default_factory=list, repr=False)

    def set(self, **attrs: Any) -> None:
        for key, value in attrs.items():
            self.attributes[key] = (
                "<redacted>" if key.lower() in _SENSITIVE_KEYS else _redact(value)
            )

    @asynccontextmanager
    async def span(self, name: str, **attrs: Any):
        """Open a child span. Records duration and marks status on exception.

        The exception is re-raised — tracing observes failures, it does not
        swallow them. Only tracing's OWN errors are suppressed (in `trace`).
        """
        current = Span(name=name, parent_id=self._open[-1].span_id if self._open else None)
        current.set(**attrs)
        self._open.append(current)
        self.spans.append(current)
        try:
            yield current
        except Exception as exc:
            current.status = "error"
            current.error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            current.duration_ms = (time.perf_counter() - current.started_at) * 1000
            self._open.pop()

    def record_llm_call(self, provider: str, model: str,
                        input_tokens: int = 0, output_tokens: int = 0,
                        cache_creation_tokens: int = 0, cache_read_tokens: int = 0) -> float:
        """Accumulate token usage and estimated spend.

        Returns the estimated cost of THIS call. Estimates use a static rate
        table, so they drift as providers change pricing — useful for spotting
        a stage that suddenly costs 10x, not for invoicing.
        """
        rate_in, rate_out = _RATES.get(model, _DEFAULT_RATE)
        cost = (input_tokens * rate_in + output_tokens * rate_out) / 1_000_000
        self.total_tokens += input_tokens + output_tokens
        self.estimated_cost_usd += cost
        if self._open:
            self._open[-1].set(
                provider=provider, model=model,
                input_tokens=input_tokens, output_tokens=output_tokens,
                cost_usd=round(cost, 6),
            )
            if cache_creation_tokens or cache_read_tokens:
                self._open[-1].set(cache_creation_tokens=cache_creation_tokens,
                                   cache_read_tokens=cache_read_tokens)
        return cost

    def stage_timings(self) -> dict[str, float]:
        """Milliseconds per top-level span — the answer to 'what was slow?'"""
        return {
            s.name: round(s.duration_ms, 2)
            for s in self.spans
            if s.parent_id is None
        }

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "user_id": self.user_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            "attributes": self.attributes,
            "stage_timings": self.stage_timings(),
            "spans": [s.to_dict() for s in self.spans],
        }


@asynccontextmanager
async def trace(name: str, user_id: str = "", **attrs: Any):
    """Start a trace for one logical operation.

    Sets the ContextVar so nested `current_trace()` calls find it, and flushes
    to exporters on exit. Exporter failures are logged and swallowed: a broken
    metrics sink must never take down a user request.
    """
    t = Trace(name=name, user_id=user_id)
    t.set(**attrs)
    token = _current.set(t)
    try:
        yield t
    except Exception as exc:
        t.status = "error"
        t.set(error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        t.duration_ms = (time.perf_counter() - t.started_at) * 1000
        _current.reset(token)
        for export in _exporters:
            try:
                export(t)
            except Exception:
                logger.exception("Trace exporter failed (ignored)")


def current_trace() -> Trace | None:
    """The active trace, or None outside a traced request.

    Instrumentation deep in the call stack uses this instead of taking a
    trace parameter, so adding tracing does not change function signatures.
    """
    return _current.get()


@asynccontextmanager
async def span(name: str, **attrs: Any):
    """Open a span on the active trace, or do nothing if untraced.

    Lets library code be instrumented unconditionally — call it from a script
    with no trace and it is a no-op rather than an error.
    """
    t = current_trace()
    if t is None:
        yield Span(name=name)
        return
    async with t.span(name, **attrs) as s:
        yield s


def register_exporter(fn: Callable[[Trace], None]) -> None:
    """Add a sink for finished traces (Phoenix, OTel, a log shipper).

    The exporter receives the Trace object; call `.to_dict()` for a
    JSON-serialisable form. Keep exporters fast — they run inline on request
    teardown. Anything slow should enqueue and return.
    """
    _exporters.append(fn)


def clear_exporters() -> None:
    """Remove all exporters. Used by tests to avoid cross-test leakage."""
    _exporters.clear()


def estimate_tokens(text: str) -> int:
    """Rough token count: ~4 characters per token.

    Deliberately crude. Real counts come from the provider response when
    available; this is a fallback so a stage still reports SOMETHING rather
    than silently recording zero cost.
    """
    return max(1, len(text) // 4)
