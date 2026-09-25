"""Tracing semantics.

These assert the three properties that make tracing safe to leave enabled in
production: it never leaks secrets, it never breaks a request, and concurrent
requests never interleave their spans.
"""
import asyncio

import pytest

from app.services.tracing import (
    clear_exporters,
    current_trace,
    estimate_tokens,
    register_exporter,
    span,
    trace,
)


@pytest.fixture(autouse=True)
def _clean_exporters():
    clear_exporters()
    yield
    clear_exporters()


async def test_spans_nest_with_correct_parents():
    async with trace("op") as t:
        async with t.span("outer"):
            async with t.span("inner"):
                pass
    outer = next(s for s in t.spans if s.name == "outer")
    inner = next(s for s in t.spans if s.name == "inner")
    assert outer.parent_id is None
    assert inner.parent_id == outer.span_id


async def test_stage_timings_only_include_top_level():
    async with trace("op") as t:
        async with t.span("a"):
            async with t.span("a-child"):
                pass
        async with t.span("b"):
            pass
    assert set(t.stage_timings()) == {"a", "b"}


async def test_secrets_are_redacted_at_every_level():
    async with trace("op") as t:
        t.set(openai_api_key="sk-REAL", user_code="secret code", keep="fine")
        async with t.span("s") as s:
            s.set(password="hunter2", nested={"token": "abc", "ok": 1})
    blob = str(t.to_dict())
    for leak in ("sk-REAL", "hunter2", "abc", "secret code"):
        assert leak not in blob, f"{leak} leaked into the trace"
    assert t.attributes["keep"] == "fine"


async def test_long_values_truncated_not_dropped():
    async with trace("op") as t:
        t.set(note="A" * 2000)
    value = t.attributes["note"]
    assert len(value) < 500
    assert value.startswith("AAA")


async def test_errors_are_recorded_and_reraised():
    with pytest.raises(ValueError):
        async with trace("op") as t:
            async with t.span("boom"):
                raise ValueError("kaboom")
    assert t.status == "error"
    assert t.spans[0].status == "error"
    assert "kaboom" in t.spans[0].error


async def test_broken_exporter_does_not_break_the_request():
    def bad(_):
        raise RuntimeError("sink down")

    register_exporter(bad)
    async with trace("op"):
        pass  # must not raise


async def test_span_outside_a_trace_is_a_noop():
    assert current_trace() is None
    async with span("orphan") as s:
        s.set(a=1)


async def test_concurrent_traces_do_not_interleave():
    async def work(prefix, n):
        async with trace(prefix) as t:
            for i in range(n):
                async with t.span(f"{prefix}-{i}"):
                    await asyncio.sleep(0.001)
            return t

    a, b = await asyncio.gather(work("A", 3), work("B", 5))
    assert all(s.name.startswith("A") for s in a.spans)
    assert all(s.name.startswith("B") for s in b.spans)
    assert len(a.spans) == 3 and len(b.spans) == 5


async def test_cost_accounting_accumulates():
    async with trace("op") as t:
        async with t.span("call"):
            cost = t.record_llm_call("openai", "gpt-4o-mini", 1_000_000, 0)
    assert cost == pytest.approx(0.15, rel=1e-3)
    assert t.total_tokens == 1_000_000


async def test_unknown_model_uses_default_rate():
    async with trace("op") as t:
        async with t.span("call"):
            t.record_llm_call("x", "some-new-model", 1_000_000, 0)
    assert t.estimated_cost_usd > 0


def test_token_estimate_is_positive():
    assert estimate_tokens("") >= 1
    assert estimate_tokens("a" * 400) == 100


async def test_trace_serialises_to_json_safe_dict():
    import json
    async with trace("op", user_id="u1") as t:
        async with t.span("s") as s:
            s.set(count=3)
    json.dumps(t.to_dict())  # must not raise
