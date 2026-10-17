"""End-to-end flow with the LLM stubbed but everything else real.

Exercises the path the UI actually walks: register → grant subscription →
submit a buggy solution → real fuzzing finds it → learning event recorded →
profile reflects it → mentor recalls their earlier reasoning.

This is the test that would have caught the wiring gap where /analyze never
wrote learning events, leaving the profile permanently empty.
"""
import pytest

from app.models.schemas import AnalysisResult
from app.services import entitlements

BUGGY_TWO_SUM = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        seen[x] = i\n"                 # inserts before checking -> reuse
    "        if target - x in seen:\n"
    "            return [seen[target - x], i]\n"
    "    return []"
)

CORRECT_TWO_SUM = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        if target - x in seen:\n"
    "            return [seen[target - x], i]\n"
    "        seen[x] = i\n"
    "    return []"
)


@pytest.fixture
def stub_llm(monkeypatch):
    async def fake_deep_review(problem_id, user_code, language, provider):
        from app.services.deep_review import gather_evidence
        evidence = await gather_evidence(problem_id, user_code, language)
        return (
            AnalysisResult(
                mistakes=[], enhancements=[], watchouts=[], interview_tips=[],
                overall_feedback="stubbed",
            ),
            evidence,
        )

    monkeypatch.setattr("app.routers.analyze.deep_review", fake_deep_review)

    async def fake_mentor(**kwargs):
        return "What happens when the two values you need are identical?"

    monkeypatch.setattr("app.routers.mentor.mentor_reply", fake_mentor)


async def _register(client, email):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    return r.json()


async def test_buggy_submission_is_caught_and_recorded(client, db, stub_llm):
    body = await _register(client, "flow1@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}

    r = await client.post("/analyze/", headers=h, json={
        "problem_id": "two-sum", "user_code": BUGGY_TWO_SUM, "language": "python",
    })
    assert r.status_code == 200
    payload = r.json()

    # Real fuzzing ran and found the reuse bug
    fuzz = payload["evidence"]["fuzz"]
    assert fuzz["ran"] is True
    assert fuzz["counterexamples"], "fuzzer did not catch the element-reuse bug"

    # The learning event was written — this is the wiring that was missing
    profile = await client.get("/mentor/profile", headers=h)
    assert profile.json()["total_attempts"] == 1
    assert profile.json()["solved"] == 0


async def test_correct_submission_records_a_solve(client, stub_llm):
    body = await _register(client, "flow2@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}

    r = await client.post("/analyze/", headers=h, json={
        "problem_id": "two-sum", "user_code": CORRECT_TWO_SUM, "language": "python",
    })
    assert r.status_code == 200
    assert not r.json()["evidence"]["fuzz"]["counterexamples"]

    profile = await client.get("/mentor/profile", headers=h)
    assert profile.json()["solved"] == 1


async def test_repeated_error_becomes_a_pattern(client, stub_llm):
    body = await _register(client, "flow3@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}

    for _ in range(2):
        await client.post("/analyze/", headers=h, json={
            "problem_id": "two-sum", "user_code": BUGGY_TWO_SUM, "language": "python",
        })

    profile = (await client.get("/mentor/profile", headers=h)).json()
    # A pattern is only reported once it has actually recurred
    assert profile["recurring_errors"], "repeated failure was not surfaced as a pattern"
    assert profile["recurring_errors"][0]["count"] >= 2
    assert profile["summary"]


async def test_single_failure_is_not_called_a_pattern(client, stub_llm):
    body = await _register(client, "flow4@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    await client.post("/analyze/", headers=h, json={
        "problem_id": "two-sum", "user_code": BUGGY_TWO_SUM, "language": "python",
    })
    profile = (await client.get("/mentor/profile", headers=h)).json()
    assert profile["recurring_errors"] == []


async def test_mentor_recalls_their_own_earlier_reasoning(client, db, stub_llm):
    body = await _register(client, "flow5@x.com")
    uid = body["user"]["id"]
    h = {"Authorization": f"Bearer {body['access_token']}"}
    await entitlements.grant(db, uid, "python", days=30)
    await db.commit()

    r = await client.post("/analyze/", headers=h, json={
        "problem_id": "contains-duplicate", "language": "python",
        "user_code": "def contains_duplicate(nums): return len(nums) != len(set(nums))",
    })
    assert r.status_code == 200
    # They reflect on a hash-map problem they solved
    await client.post("/mentor/reflect", headers=h, params={
        "problem_id": "contains-duplicate",
        "reasoning": "I needed to know if I'd seen a value before, so I used a set.",
        "language": "python",
    })

    # Now stuck on two-sum, which shares the hash-map tag
    r = await client.post("/mentor/ask", headers=h, json={
        "problem_id": "two-sum", "language": "python",
        "reasoning": "I'm using two nested loops and it feels slow.",
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload["hint_tier"] == 1
    assert payload["recalled_moment"], "mentor did not recall their earlier reasoning"
    assert "contains-duplicate" in payload["recalled_moment"]


async def test_hint_tier_escalates_only_on_repeat_asks(client, db, stub_llm):
    body = await _register(client, "flow6@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    await entitlements.grant(db, body["user"]["id"], "python", days=30)
    await db.commit()

    tiers = []
    for _ in range(5):
        r = await client.post("/mentor/ask", headers=h, json={
            "problem_id": "two-sum", "language": "python",
            "reasoning": "still stuck",
        })
        tiers.append(r.json()["hint_tier"])

    assert tiers == [1, 2, 3, 4, 4], f"unexpected escalation: {tiers}"


async def test_step_back_offered_at_top_tier(client, db, stub_llm):
    body = await _register(client, "flow7@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    await entitlements.grant(db, body["user"]["id"], "python", days=30)
    await db.commit()

    offer = None
    for _ in range(4):
        r = await client.post("/mentor/ask", headers=h, json={
            "problem_id": "two-sum", "language": "python", "reasoning": "stuck",
        })
        offer = r.json()["step_back_offer"]
    # At the top tier the learner must have somewhere to go that isn't the answer
    assert offer is not None
    assert offer["easier_problem"] or offer["concept"]


async def test_mentor_charges_peppercorns_per_turn(client, db, stub_llm):
    body = await _register(client, "flow8@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    start = body["user"]["peppercorns"]
    await entitlements.grant(db, body["user"]["id"], "python", days=30)
    await db.commit()

    r = await client.post("/mentor/ask", headers=h, json={
        "problem_id": "two-sum", "language": "python", "reasoning": "thinking",
    })
    from app.core.config import settings
    assert r.json()["peppercorns_remaining"] == start - settings.mentor_cost
