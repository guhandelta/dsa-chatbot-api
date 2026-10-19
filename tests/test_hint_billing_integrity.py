"""Billing facts survive profile erasure; tier reservations survive overlap."""
import asyncio
import pytest

from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import HintUsage, LearningEvent, User
from app.routers.mentor import _current_tier
from app.services import rewards
from tests.test_mentor_pricing_rewards import register, stub_mentor


async def test_overlapping_hints_reserve_distinct_tiers(client, db, monkeypatch):
    headers, uid = await register(client, db, "overlap@example.com")
    db.add(LearningEvent(user_id=uid, problem_id="two-sum", language="python", kind="hint", hint_tier=1))
    await db.commit()
    entered, release = asyncio.Event(), asyncio.Event()

    async def reply(**kw):
        if kw["reasoning"] == "first":
            entered.set()
            await asyncio.wait_for(release.wait(), 10)
        return "Which property matters?"

    monkeypatch.setattr("app.routers.mentor.mentor_reply", reply)
    body = {"problem_id": "two-sum", "language": "python", "reasoning": "first"}
    first = asyncio.create_task(client.post("/mentor/ask", headers=headers, json=body))
    await asyncio.wait_for(entered.wait(), 10)
    try:
        second = await client.post("/mentor/ask", headers=headers, json={**body, "reasoning": "second"})
    finally:
        release.set()
    first = await first
    assert first.status_code == second.status_code == 200
    assert [(r.json()["hint_tier"], r.json()["peppercorns_charged"]) for r in (first, second)] == [
        (2, 0), (3, settings.mentor_cost)]
    assert await _current_tier(db, uid, "two-sum") == 4


async def test_profile_erasure_preserves_billing_and_independent_solve_eligibility(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, uid = await register(client, db, "erase-billing@example.com")
    body = {"problem_id": "two-sum", "language": "python", "reasoning": "a map"}
    for tier in (1, 2, 3):
        result = await client.post("/mentor/ask", headers=headers, json=body)
        assert result.status_code == 200 and result.json()["hint_tier"] == tier
    assert (await client.delete("/mentor/profile", headers=headers)).status_code == 200
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id == uid)) == 0
    assert await _current_tier(db, uid, "two-sum") == 4
    assert await rewards.independent_solve(db, uid, "two-sum", "python") is None
    result = await client.post("/mentor/ask", headers=headers, json=body)
    assert result.json()["hint_tier"] == 4 and result.json()["peppercorns_charged"] == settings.mentor_cost


async def test_erasure_also_preserves_legacy_hint_events(client, db):
    headers, uid = await register(client, db, "legacy-billing@example.com")
    for tier in (1, 2, 3):
        db.add(LearningEvent(user_id=uid, problem_id="two-sum", language="python", kind="hint", hint_tier=tier))
    await db.commit()
    await client.delete("/mentor/profile", headers=headers)
    assert await _current_tier(db, uid, "two-sum") == 4
    assert await db.scalar(select(func.count()).select_from(HintUsage).where(HintUsage.user_id == uid)) == 3


async def test_stale_free_price_is_rejected_before_spending_or_generation(client, db, monkeypatch):
    headers, uid = await register(client, db, "stale-price@example.com")
    for tier in (1, 2):
        db.add(LearningEvent(user_id=uid, problem_id="two-sum", language="python", kind="hint", hint_tier=tier))
    await db.commit()

    async def forbidden(**kw):
        raise AssertionError("A changed price must not generate a hint")

    monkeypatch.setattr("app.routers.mentor.mentor_reply", forbidden)
    response = await client.post("/mentor/ask", headers=headers, json={
        "problem_id": "two-sum", "language": "python", "reasoning": "a map", "max_hint_cost": 0})
    assert response.status_code == 409 and "price has changed" in response.json()["detail"]
    assert await db.scalar(select(User.peppercorns).where(User.id == uid)) == settings.signup_bonus
    assert await _current_tier(db, uid, "two-sum") == 3


@pytest.mark.parametrize("prior_hints", [0, 2])
async def test_failed_generation_does_not_consume_reserved_tier(client, db, monkeypatch, prior_hints):
    headers, uid = await register(client, db, "failed-tier@example.com")
    for tier in range(1, prior_hints + 1):
        db.add(LearningEvent(user_id=uid, problem_id="two-sum", language="python", kind="hint", hint_tier=tier))
    await db.commit()

    async def failed(**kw):
        raise RuntimeError("offline provider")

    monkeypatch.setattr("app.routers.mentor.mentor_reply", failed)
    response = await client.post("/mentor/ask", headers=headers, json={
        "problem_id": "two-sum", "language": "python", "reasoning": "a map"})
    assert response.status_code == 502
    assert await _current_tier(db, uid, "two-sum") == prior_hints + 1
    assert await db.scalar(select(User.peppercorns).where(User.id == uid)) == settings.signup_bonus


async def test_receipt_replay_does_not_reserve_another_tier(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, uid = await register(client, db, "replay-tier@example.com")
    headers["Idempotency-Key"] = "same-hint"
    body = {"problem_id": "two-sum", "language": "python", "reasoning": "a map", "max_hint_cost": 0}
    first = await client.post("/mentor/ask", headers=headers, json=body)
    second = await client.post("/mentor/ask", headers=headers, json=body)
    assert first.status_code == second.status_code == 200 and first.json() == second.json()
    assert await db.scalar(select(func.count()).select_from(HintUsage).where(HintUsage.user_id == uid)) == 1
    assert await _current_tier(db, uid, "two-sum") == 2


async def test_practice_enforces_advertised_price_and_unlocks_after_conflict(client, db, monkeypatch):
    stub_mentor(monkeypatch)
    headers, uid = await register(client, db, "practice-price@example.com")
    pid, lang = "javascript-path-01-values", "javascript"
    for tier in (1, 2):
        db.add(LearningEvent(user_id=uid, problem_id=pid, language=lang, kind="hint", hint_tier=tier))
    await db.commit()
    started = await client.post("/practice/sessions", headers=headers, json={"problem_id": pid, "language": lang})
    endpoint = f"/practice/sessions/{started.json()['session_id']}/actions"
    body = {"action": "hint", "reasoning": "multiply the quantities", "max_hint_cost": 0}
    rejected = await client.post(endpoint, headers=headers, json=body)
    assert rejected.status_code == 409 and "price has changed" in rejected.json()["detail"]
    assert await db.scalar(select(User.peppercorns).where(User.id == uid)) == settings.signup_bonus
    accepted = await client.post(endpoint, headers=headers, json={**body, "max_hint_cost": settings.mentor_cost})
    assert accepted.status_code == 200 and accepted.json()["hint_tier"] == 3
    assert accepted.json()["peppercorns_charged"] == settings.mentor_cost


async def test_erasure_during_generation_does_not_restore_personal_reasoning(client, db, monkeypatch):
    headers, uid = await register(client, db, "erase-pending@example.com")
    entered, release = asyncio.Event(), asyncio.Event()

    async def reply(**kw):
        entered.set()
        await asyncio.wait_for(release.wait(), 10)
        return "Which property matters?"

    monkeypatch.setattr("app.routers.mentor.mentor_reply", reply)
    body = {"problem_id": "two-sum", "language": "python", "reasoning": "reasoning to erase"}
    task = asyncio.create_task(client.post("/mentor/ask", headers=headers, json=body))
    await asyncio.wait_for(entered.wait(), 10)
    try:
        assert (await client.delete("/mentor/profile", headers=headers)).status_code == 200
    finally:
        release.set()
    assert (await task).status_code == 200
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id == uid)) == 0
    assert await _current_tier(db, uid, "two-sum") == 2
