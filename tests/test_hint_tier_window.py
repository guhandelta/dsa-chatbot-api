"""Hint tiers must reset after the configured cycle.

Without a window, tier only ratchets upward: a learner returning to a problem
after six weeks would be handed the strongest hint immediately, which defeats the
Socratic design.
"""
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.models import LearningEvent
from app.routers.mentor import _current_tier
from app.services.mentor import MAX_TIER


async def _hint(db, user_id, problem_id, hours_ago):
    db.add(LearningEvent(
        user_id=user_id, problem_id=problem_id, kind="hint", language="python",
        hint_tier=1, created_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
    ))
    await db.commit()


async def test_first_ask_is_tier_one(db):
    assert await _current_tier(db, "u1", "two-sum") == 1


async def test_tier_escalates_within_a_session(db):
    await _hint(db, "u2", "two-sum", 0.1)
    assert await _current_tier(db, "u2", "two-sum") == 2
    await _hint(db, "u2", "two-sum", 0.1)
    assert await _current_tier(db, "u2", "two-sum") == 3


async def test_tier_is_clamped_at_max(db):
    for _ in range(10):
        await _hint(db, "u3", "two-sum", 0.1)
    assert await _current_tier(db, "u3", "two-sum") == MAX_TIER


async def test_tier_resets_after_the_window(db, monkeypatch):
    monkeypatch.setattr(settings, "hint_tier_reset_hours", 1008)
    for _ in range(6):
        await _hint(db, "u4", "two-sum", 1009)     # outside six weeks
    assert await _current_tier(db, "u4", "two-sum") == 1, "stale hints must not carry over"


async def test_window_boundary(db, monkeypatch):
    monkeypatch.setattr(settings, "hint_tier_reset_hours", 1008)
    await _hint(db, "u5", "two-sum", 1007.9)       # inside
    assert await _current_tier(db, "u5", "two-sum") == 2
    await _hint(db, "u6", "two-sum", 1008.1)       # outside
    assert await _current_tier(db, "u6", "two-sum") == 1


async def test_tiers_are_isolated_per_problem(db):
    for _ in range(3):
        await _hint(db, "u7", "two-sum", 0.1)
    await _hint(db, "u7", "3sum", 0.1)
    assert await _current_tier(db, "u7", "two-sum") == 4
    assert await _current_tier(db, "u7", "3sum") == 2


async def test_tiers_are_isolated_per_user(db):
    for _ in range(3):
        await _hint(db, "a", "two-sum", 0.1)
    await _hint(db, "b", "two-sum", 0.1)
    assert await _current_tier(db, "a", "two-sum") == 4
    assert await _current_tier(db, "b", "two-sum") == 2
