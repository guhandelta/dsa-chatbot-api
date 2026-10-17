"""Bounded, restart-safe housekeeping. No prices or entitlement policy here."""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from app.db.models import PracticeSession, ServiceOperation, VectorCleanupJob
from app.services.peppercorns import credit

logger = logging.getLogger(__name__)


def queue_cleanup(session, ids):
    if ids:
        session.add(VectorCleanupJob(chunk_ids=json.dumps(ids)))


async def drain_cleanup(session, limit=20):
    from app.services.knowledge_base import remove_chunks
    jobs = list((await session.scalars(select(VectorCleanupJob).order_by(VectorCleanupJob.created_at).limit(limit))).all())
    removed = 0
    for job in jobs:
        try:
            await asyncio.to_thread(remove_chunks, json.loads(job.chunk_ids))
        except Exception as exc:
            job.attempts += 1
            # Store only exception type, never API keys or provider payloads.
            job.last_error = type(exc).__name__[:200]
        else:
            await session.delete(job)
            removed += 1
    await session.commit()
    return removed


async def recover_expired(session, limit=100, now=None, user_id=None, scope=None):
    """Only a winning CAS may refund. Safe across retries/multiple workers."""
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(minutes=30)
    stmt = select(ServiceOperation).where(ServiceOperation.state == "running", ServiceOperation.created_at < cutoff)
    if user_id is not None:
        stmt = stmt.where(ServiceOperation.user_id == user_id)
    if scope is not None:
        stmt = stmt.where(ServiceOperation.scope == scope)
    rows = list((await session.scalars(stmt.order_by(ServiceOperation.created_at).limit(limit))).all())
    recovered = 0
    for row in rows:
        amount = (await session.execute(update(ServiceOperation).where(
            ServiceOperation.id == row.id, ServiceOperation.state == "running"
        ).values(state="failed", http_status=503, response_json=json.dumps({"detail":
            "The interrupted request expired. Its reserved peppercorns were refunded."
        })).returning(ServiceOperation.amount))).scalar_one_or_none()
        if amount is None:
            continue
        if amount:
            await credit(session, row.user_id, amount, "refund:" + row.reason)
        if row.scope.startswith("practice:") and row.scope != "practice:start":
            await session.execute(update(PracticeSession).where(
                PracticeSession.id == row.scope[len("practice:"):],
                PracticeSession.user_id == row.user_id,
                # The old worker must not unlock a newer action.
                PracticeSession.busy_token == row.id
            ).values(busy=False, busy_token=""))
        recovered += 1
    await session.commit()
    return recovered


async def run_once(factory=None):
    if factory is None:
        from app.db.database import SessionLocal
        factory = SessionLocal
    async with factory() as session:
        recovered = await recover_expired(session)
        cleaned = await drain_cleanup(session)
    return {"recovered": recovered, "cleanup_jobs_completed": cleaned}


async def worker():
    while True:
        try:
            await run_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Maintenance pass failed; it will retry")
        await asyncio.sleep(60)
