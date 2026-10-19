"""Earn-back peppercorns for independent work.

Rewards follow the mentor's design: it never hands out solutions, so the
economy pays learners for working things out themselves rather than only
charging them for help.

  - solving a problem for the first time without the paid hint tiers
  - each `reward_streak_days`-day run of consecutive active days
  - completing a curriculum stage

Every grant is keyed and recorded in `reward_grants` with a unique
(user, key) constraint, so a retried request or a recomputed progress view can
never pay twice. Callers own the transaction boundary, as with `credit`.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import LearningEvent, RewardGrant
from app.services.peppercorns import credit


async def grant_once(session: AsyncSession, user_id: str, key: str, amount: int, reason: str) -> dict | None:
    """Credit `amount` once per (user, key). Returns the grant, or None if it
    was already paid or the reward is disabled."""
    if amount <= 0:
        return None
    if await session.scalar(select(RewardGrant.id).where(
            RewardGrant.user_id == user_id, RewardGrant.key == key)):
        return None
    try:
        async with session.begin_nested():
            session.add(RewardGrant(user_id=user_id, key=key, amount=amount))
            await session.flush()
    except IntegrityError:
        return None  # a concurrent request won the same grant
    balance = await credit(session, user_id, amount, reason)
    return {"key": key, "amount": amount, "reason": reason, "balance": balance}


async def has_solved(session: AsyncSession, user_id: str, problem_id: str, language: str) -> bool:
    return bool(await session.scalar(select(LearningEvent.id).where(
        LearningEvent.user_id == user_id, LearningEvent.problem_id == problem_id,
        LearningEvent.language == language, LearningEvent.kind == "solved").limit(1)))


async def independent_solve(session: AsyncSession, user_id: str, problem_id: str, language: str) -> dict | None:
    """First solve of a problem in a language, without any paid-tier hint."""
    paid_hints = await session.scalar(select(func.count()).select_from(LearningEvent).where(
        LearningEvent.user_id == user_id, LearningEvent.problem_id == problem_id,
        LearningEvent.language == language, LearningEvent.kind == "hint",
        LearningEvent.hint_tier > settings.free_hint_tiers))
    if paid_hints:
        return None
    return await grant_once(session, user_id, f"solve:{language}:{problem_id}",
                            settings.reward_independent_solve, "earn:independent_solve")


def _day(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).date()


async def active_run(session: AsyncSession, user_id: str, today: date | None = None) -> int:
    """Consecutive UTC days with learning activity, ending today."""
    today = today or datetime.now(timezone.utc).date()
    since = datetime.combine(today - timedelta(days=366), datetime.min.time(), tzinfo=timezone.utc)
    stamps = (await session.scalars(select(LearningEvent.created_at).where(
        LearningEvent.user_id == user_id, LearningEvent.created_at >= since))).all()
    days = {_day(t) for t in stamps}
    run = 0
    while today - timedelta(days=run) in days:
        run += 1
    return run


async def streak(session: AsyncSession, user_id: str, today: date | None = None) -> dict | None:
    """Pay once each time the active run reaches a multiple of the streak length."""
    today = today or datetime.now(timezone.utc).date()
    run = await active_run(session, user_id, today)
    if run == 0 or run % settings.reward_streak_days:
        return None
    return await grant_once(session, user_id, f"streak:{today.isoformat()}",
                            settings.reward_streak, "earn:streak")


async def after_solve(session: AsyncSession, user_id: str, problem_id: str, language: str,
                      *, first_solve: bool) -> list[dict]:
    """Rewards that a passing evaluation can unlock. Call after recording it."""
    earned = []
    if first_solve:
        earned.append(await independent_solve(session, user_id, problem_id, language))
    earned.append(await streak(session, user_id))
    return [e for e in earned if e]
