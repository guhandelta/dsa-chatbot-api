# Entitlements, the Socratic gate, and learning-profile behaviour.
from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from app.services import entitlements
from app.services.learning_profile import LearningProfile, categorize_failure
from app.services.mentor import MAX_TIER, TIERS


def _fuzz(args, student, reference):
    return {"fuzz": {"counterexamples": [
        {"args": args, "student_output": student, "reference_output": reference}
    ]}}


@pytest.mark.parametrize("args,student,reference,expected", [
    ([[-2, -41], -4], [0, 0], [], "element_reuse"),
    ([[-20]], 0, -20, "all_negative"),
    ([[14], 14], -1, 0, "single_element"),
    ([[4, -6, -5]], 30, 120, "negative_values"),
    ([[-7, -1, -7]], False, True, "duplicate_values"),
    ([[]], None, 0, "empty_input"),
])
def test_error_categorisation_is_deterministic(args, student, reference, expected):
    category, _ = categorize_failure(_fuzz(args, student, reference))
    assert category == expected


def test_clean_run_has_no_category():
    assert categorize_failure({"fuzz": {"ran": True, "counterexamples": []}})[0] == ""


def test_timeout_detected_from_curated_run():
    ev = {"curated": {"results": [
        {"tier": 1, "status": "failed", "passed_cases": 0, "detail": "Timed out after 8s"}
    ]}}
    assert categorize_failure(ev)[0] == "timeout"


def test_profile_summary_describes_behaviour_not_the_person():
    p = LearningProfile(
        total_attempts=10, solved=4,
        recurring_errors=[("empty_input", 4)],
        weak_algorithms=[("dynamic-programming", 3)],
        strong_algorithms=[("hash-map", 3)],
    )
    summary = p.summary().lower()
    assert "empty" in summary
    # must never characterise the learner themselves
    for word in ("careless", "sloppy", "weak thinker", "you are a", "lazy", "poor"):
        assert word not in summary


def test_empty_profile_makes_no_claims():
    assert "not enough" in LearningProfile().summary().lower()


def test_hint_tiers_never_reach_a_solution():
    for _, (label, instruction) in TIERS.items():
        text = (label + instruction).lower()
        assert "write the solution" not in text
        assert "give them the code" not in text
    # top tier names a technique family but still asks a question
    assert "never write" in TIERS[MAX_TIER][1].lower()


# ---------------- entitlements ----------------

async def _reg(client, email):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    return r.json()


async def test_mentor_requires_subscription(client):
    body = await _reg(client, "nosub@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.post("/mentor/ask", headers=h, json={
        "problem_id": "two-sum", "language": "python",
        "reasoning": "I think I need a nested loop",
    })
    assert r.status_code == 402
    assert "subscription" in r.json()["detail"].lower()


async def test_entitlement_is_per_language(client, db):
    body = await _reg(client, "perlang@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    await entitlements.grant(db, body["user"]["id"], "python", days=30)
    await db.commit()

    py = await client.get("/mentor/entitlement?language=python", headers=h)
    assert py.json()["entitled"] is True
    rust = await client.get("/mentor/entitlement?language=rust", headers=h)
    assert rust.json()["entitled"] is False


async def test_expired_subscription_does_not_entitle(client, db):
    from app.db.models import Subscription
    body = await _reg(client, "expired@x.com")
    db.add(Subscription(
        user_id=body["user"]["id"], language="python", status="active",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    ))
    await db.commit()
    decision = await entitlements.check(db, body["user"]["id"], "python")
    assert decision["entitled"] is False


async def test_renewal_extends_rather_than_duplicating(client, db):
    body = await _reg(client, "renew@x.com")
    uid = body["user"]["id"]
    first = await entitlements.grant(db, uid, "python", days=30)
    await db.commit()
    first_expiry = first.expires_at

    await entitlements.grant(db, uid, "python", days=30)
    await db.commit()
    subs = await entitlements.list_for(db, uid)
    assert len(subs) == 1, "renewal created a duplicate entitlement"
    assert subs[0].expires_at > first_expiry


async def test_cancellation_keeps_paid_time(client, db):
    body = await _reg(client, "cancel@x.com")
    uid = body["user"]["id"]
    await entitlements.grant(db, uid, "python", days=30)
    await db.commit()
    assert await entitlements.revoke(db, uid, "python") is True
    await db.commit()
    subs = await entitlements.list_for(db, uid)
    assert subs[0].status == "cancelled"
    # time already paid for is not confiscated
    assert subs[0].expires_at > datetime.now(timezone.utc).replace(tzinfo=subs[0].expires_at.tzinfo)


async def test_webhook_refuses_without_configured_secret(client, monkeypatch):
    monkeypatch.setattr(settings, "stripe_webhook_secret", "")
    r = await client.post("/subscriptions/webhook", json={"type": "x"})
    assert r.status_code == 503


async def test_webhook_refuses_without_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    r = await client.post("/subscriptions/webhook", json={"type": "x"})
    assert r.status_code == 400


async def test_profile_export_and_delete(client):
    body = await _reg(client, "priv@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    exported = await client.get("/mentor/profile/export", headers=h)
    assert exported.status_code == 200
    assert "profile" in exported.json() and "events" in exported.json()
    deleted = await client.delete("/mentor/profile", headers=h)
    assert deleted.status_code == 200
