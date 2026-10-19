"""Reserve hint tiers under the operations user lock, before generation."""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import or_, select

from app.core.config import settings
from app.db.models import HintUsage, LearningEvent, ServiceOperation


def valid_usage(*, include_pending=True):
    completed = ServiceOperation.state == "completed"
    if include_pending:
        completed = or_(completed, (ServiceOperation.state == "running") & (
            ServiceOperation.created_at >= datetime.now(timezone.utc) - timedelta(minutes=30)))
    return or_(HintUsage.operation_id.is_(None), completed)


async def current_tier(session, user_id, problem_id, language="python", *, now=None):
    from app.services.mentor import MAX_TIER
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    uses = select(HintUsage.created_at).outerjoin(
        ServiceOperation, ServiceOperation.id == HintUsage.operation_id).where(
        HintUsage.user_id == user_id, HintUsage.problem_id == problem_id,
        HintUsage.language == language, HintUsage.created_at <= now, valid_usage())
    # Compatibility with historic/imported events. Migrations backfill existing
    # events; excluding linked IDs also supports events inserted by older tools.
    legacy = select(LearningEvent.created_at).where(
        LearningEvent.user_id == user_id, LearningEvent.problem_id == problem_id,
        LearningEvent.language == language, LearningEvent.kind == "hint",
        LearningEvent.created_at <= now,
        ~select(HintUsage.id).where(HintUsage.event_id == LearningEvent.id).exists())
    times = list((await session.scalars(uses.union_all(legacy))).all())
    if not times:
        return 1
    times = [t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t for t in times]
    duration = timedelta(hours=settings.hint_tier_reset_hours)
    anchor = min(times)
    cycle_start = anchor + ((now - anchor) // duration) * duration
    return min(sum(t >= cycle_start for t in times) + 1, MAX_TIER)


async def reserve(session, user_id, problem_id, language, operation_id, max_cost=None):
    """Caller holds the operations user lock through the reservation commit."""
    from app.services.mentor import hint_cost
    tier = await current_tier(session, user_id, problem_id, language)
    cost = hint_cost(tier)
    if max_cost is not None and cost > max_cost:
        raise HTTPException(409, "The hint price has changed. Review the current price and try again.")
    session.add(HintUsage(user_id=user_id, problem_id=problem_id, language=language,
                          tier=tier, operation_id=operation_id))
    return tier, cost


async def preserve_legacy(session, user_id):
    """Retain billing facts before erasing personal reasoning and quiz data."""
    events = (await session.scalars(select(LearningEvent).where(
        LearningEvent.user_id == user_id, LearningEvent.kind == "hint",
        ~select(HintUsage.id).where(HintUsage.event_id == LearningEvent.id).exists()))).all()
    for event in events:
        session.add(HintUsage(user_id=user_id, problem_id=event.problem_id,
                              language=event.language, tier=event.hint_tier,
                              event_id=event.id, created_at=event.created_at))
    await session.flush()
