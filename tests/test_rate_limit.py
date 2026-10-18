"""Rate limiting.

Counts DEBITS, not learning events. Two regression tests below exist because
an earlier implementation counted learning events and had both defects:

  * passing submissions recorded kind="solved" and so were never counted
  * the event was written after the pipeline, so concurrent requests all
    passed the check before any of them registered

Both are asserted directly so neither can come back.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from app.db.models import Transaction
from app.services.rate_limit import (
    RateLimitExceeded,
    count_recent,
    enforce_rate_limit,
)


async def _debits(db, user_id: str, reason: str, n: int, hours_ago: float = 0.1):
    when = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    for _ in range(n):
        db.add(Transaction(
            user_id=user_id, amount=-1, balance_after=0,
            reason=reason, created_at=when,
        ))
    await db.commit()


async def test_under_limit_passes(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 30)
    await _debits(db, "u1", "analyze", 29)
    await enforce_rate_limit(db, "u1", "attempt")


async def test_at_limit_is_rejected(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 30)
    await _debits(db, "u2", "analyze", 30)
    with pytest.raises(RateLimitExceeded) as exc:
        await enforce_rate_limit(db, "u2", "attempt")
    assert "no peppercorns" in str(exc.value).lower()


async def test_passing_submissions_still_count(db, monkeypatch):
    """REGRESSION: a correct solution debits exactly like a failing one, so it
    must consume budget. The previous implementation counted only failed
    attempts, leaving the expensive happy path entirely uncapped."""
    monkeypatch.setattr(settings, "submissions_per_hour", 3)
    await _debits(db, "u3", "analyze", 3)     # all successful reviews
    with pytest.raises(RateLimitExceeded):
        await enforce_rate_limit(db, "u3", "attempt")


async def test_debit_commits_before_work_so_counting_is_prompt(db, monkeypatch):
    """REGRESSION: the counter must reflect a request as soon as its debit
    commits, not after the pipeline finishes."""
    monkeypatch.setattr(settings, "submissions_per_hour", 2)
    await _debits(db, "u4", "analyze", 1)
    assert await count_recent(db, "u4", "attempt") == 1
    await _debits(db, "u4", "analyze", 1)
    assert await count_recent(db, "u4", "attempt") == 2
    with pytest.raises(RateLimitExceeded):
        await enforce_rate_limit(db, "u4", "attempt")


async def test_refunds_do_not_consume_budget(db, monkeypatch):
    """A request that failed and was refunded should not count against the
    user — they got nothing for it."""
    monkeypatch.setattr(settings, "submissions_per_hour", 5)
    await _debits(db, "u5", "analyze", 2)
    db.add(Transaction(user_id="u5", amount=5, balance_after=0,
                       reason="refund:analyze"))
    await db.commit()
    assert await count_recent(db, "u5", "attempt") == 2


async def test_admin_credits_do_not_inflate_usage(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 5)
    db.add(Transaction(user_id="u6", amount=1000, balance_after=1000,
                       reason="admin:local_access"))
    await db.commit()
    assert await count_recent(db, "u6", "attempt") == 0


async def test_old_debits_age_out(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 30)
    await _debits(db, "u7", "analyze", 50, hours_ago=2.0)
    assert await count_recent(db, "u7", "attempt") == 0
    await enforce_rate_limit(db, "u7", "attempt")


async def test_budgets_are_separate_per_action(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 5)
    monkeypatch.setattr(settings, "hints_per_hour", 60)
    await _debits(db, "u8", "analyze", 5)
    with pytest.raises(RateLimitExceeded):
        await enforce_rate_limit(db, "u8", "attempt")
    await enforce_rate_limit(db, "u8", "hint")   # mentor unaffected


async def test_mentor_budget_enforced_independently(db, monkeypatch):
    monkeypatch.setattr(settings, "hints_per_hour", 4)
    await _debits(db, "u9", "mentor", 4)
    with pytest.raises(RateLimitExceeded) as exc:
        await enforce_rate_limit(db, "u9", "hint")
    assert "mentor questions" in str(exc.value)


async def test_users_do_not_affect_each_other(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 3)
    await _debits(db, "noisy", "analyze", 5)
    await enforce_rate_limit(db, "quiet", "attempt")


async def test_zero_limit_disables_the_check(db, monkeypatch):
    monkeypatch.setattr(settings, "submissions_per_hour", 0)
    await _debits(db, "u10", "analyze", 500)
    await enforce_rate_limit(db, "u10", "attempt")


async def test_rate_limited_request_returns_429_and_no_charge(client, db, monkeypatch, subscribe_user):
    monkeypatch.setattr(settings, "submissions_per_hour", 1)
    r = await client.post("/auth/register",
                          json={"email": "rl@x.com", "password": "password123"})
    body = r.json()
    await subscribe_user(r.json()["user"]["id"], "python")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    start = body["user"]["peppercorns"]
    await _debits(db, body["user"]["id"], "analyze", 1)

    res = await client.post("/analyze/", headers=h, json={
        "problem_id": "two-sum",
        "user_code": "def two_sum(nums, target):\n    return []",
        "language": "python",
    })
    assert res.status_code == 429
    me = await client.get("/auth/me", headers=h)
    assert me.json()["peppercorns"] == start, "a rate-limited request must not charge"
