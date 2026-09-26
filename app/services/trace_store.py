"""Persistence for finished traces.

Kept separate from `tracing.py` so the tracing primitives stay dependency-free
and unit-testable without a database. This module is the only place that knows
traces are stored in SQL at all.
"""
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TraceRecord
from app.services.tracing import Trace

logger = logging.getLogger(__name__)


async def save(session: AsyncSession, t: Trace) -> None:
    """Persist one finished trace.

    Failures are logged and swallowed: losing a trace is acceptable, failing
    a user's request because the trace could not be written is not.
    """
    try:
        payload = t.to_dict()
        session.add(TraceRecord(
            trace_id=t.trace_id,
            name=t.name,
            user_id=t.user_id,
            duration_ms=t.duration_ms,
            status=t.status,
            total_tokens=t.total_tokens,
            estimated_cost_usd=t.estimated_cost_usd,
            payload=json.dumps(payload, default=str)[:200_000],
        ))
        await session.commit()
    except Exception:
        logger.exception("Failed to persist trace %s (ignored)", t.trace_id)


async def recent(session: AsyncSession, limit: int = 50, name: str | None = None,
                 status: str | None = None, user_id: str | None = None) -> list[dict]:
    stmt = select(TraceRecord).order_by(TraceRecord.created_at.desc()).limit(limit)
    if name:
        stmt = stmt.where(TraceRecord.name == name)
    if status:
        stmt = stmt.where(TraceRecord.status == status)
    if user_id:
        stmt = stmt.where(TraceRecord.user_id == user_id)
    rows = (await session.execute(stmt)).scalars()
    return [
        {
            "trace_id": r.trace_id, "name": r.name, "status": r.status,
            "duration_ms": r.duration_ms, "total_tokens": r.total_tokens,
            "estimated_cost_usd": round(r.estimated_cost_usd, 6),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


async def detail(session: AsyncSession, trace_id: str) -> dict | None:
    stmt = select(TraceRecord).where(TraceRecord.trace_id == trace_id)
    row = (await session.execute(stmt)).scalar_one_or_none()
    return json.loads(row.payload) if row else None


async def summary(session: AsyncSession, limit: int = 500) -> dict:
    """Aggregate view: where is time going, what does each operation cost,
    and what is failing. This is the question tracing exists to answer."""
    stmt = select(TraceRecord).order_by(TraceRecord.created_at.desc()).limit(limit)
    rows = list((await session.execute(stmt)).scalars())
    if not rows:
        return {"traces": 0, "operations": [], "note": "No traces recorded yet."}

    buckets: dict[str, dict] = {}
    for r in rows:
        b = buckets.setdefault(r.name, {
            "operation": r.name, "count": 0, "errors": 0,
            "total_ms": 0.0, "total_cost": 0.0, "total_tokens": 0,
            "durations": [], "stage_ms": {},
        })
        b["count"] += 1
        b["errors"] += 1 if r.status == "error" else 0
        b["total_ms"] += r.duration_ms
        b["total_cost"] += r.estimated_cost_usd
        b["total_tokens"] += r.total_tokens
        b["durations"].append(r.duration_ms)
        try:
            for stage, ms in (json.loads(r.payload).get("stage_timings") or {}).items():
                b["stage_ms"][stage] = b["stage_ms"].get(stage, 0.0) + ms
        except Exception:
            pass

    operations = []
    for b in buckets.values():
        durations = sorted(b["durations"])
        n = len(durations)
        p95 = durations[min(int(n * 0.95), n - 1)]
        operations.append({
            "operation": b["operation"],
            "count": b["count"],
            "error_rate": round(b["errors"] / b["count"], 3),
            "avg_ms": round(b["total_ms"] / b["count"], 1),
            "p95_ms": round(p95, 1),
            "avg_cost_usd": round(b["total_cost"] / b["count"], 6),
            "avg_tokens": int(b["total_tokens"] / b["count"]),
            # Average ms per stage — the 'what was slow?' answer
            "stage_breakdown": {
                k: round(v / b["count"], 1)
                for k, v in sorted(b["stage_ms"].items(), key=lambda kv: -kv[1])
            },
        })
    operations.sort(key=lambda o: -o["count"])
    return {
        "traces": len(rows),
        "total_estimated_cost_usd": round(sum(r.estimated_cost_usd for r in rows), 4),
        "operations": operations,
    }


async def prune(session: AsyncSession, older_than_days: int) -> int:
    """Delete old traces. Traces accumulate quickly; retention is deliberate
    rather than automatic so an operator decides the policy."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    result = await session.execute(
        delete(TraceRecord).where(TraceRecord.created_at < cutoff)
    )
    await session.commit()
    return result.rowcount or 0
