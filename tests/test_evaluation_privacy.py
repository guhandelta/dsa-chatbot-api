"""Hidden test values must never reach a learner through a paid evaluation:
not in the response, not in the stored session, not in the review prompts."""
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.db.models import Subscription
from app.models.schemas import AnalysisResult
from app.services.content_catalog import load_test_cases
from app.services.evidence_safety import learner_safe, mask

PID = "python-path-01-values"
WRONG = "def total_cost(price, quantity):\n    return price + quantity\n"
# Expected values unique enough that finding them anywhere means a leak.
HIDDEN = ("1000000", "expected 12", "expected 42")


def test_masking_and_redaction_keep_diagnostics_but_drop_values():
    assert mask("case 1: got 7, expected 12; case 2: got [1], expected [2, 3]") == \
        "case 1: wrong answer; case 2: wrong answer"
    assert mask("TypeError: f() got an unexpected keyword argument 'x'") == \
        "TypeError: f() got an unexpected keyword argument 'x'"
    cases, expected, _, _ = load_test_cases(PID)
    raw = {"curated": {"results": [{
        "language": "python", "tier": 1, "status": "failed", "passed_cases": 1, "total_cases": len(cases),
        "detail": "case 1: got 7, expected 12", "outputs": [7, 0, 0, 1, 2000, 13], "evidence": {}}]},
        "fuzz": None, "complexity": None}
    safe = learner_safe(raw, PID)
    result = safe["curated"]["results"][0]
    assert result["outputs"] == [] and result["detail"] == f"1/{len(cases)} test cases passed"
    assert result["case_results"] == [o == e for o, e in zip([7, 0, 0, 1, 2000, 13], expected)]
    assert raw["curated"]["results"][0]["outputs"]  # the original is untouched
    assert learner_safe(safe, PID) == safe  # idempotent
    crash = {"curated": {"results": [{"language": "python", "tier": 1, "status": "failed", "passed_cases": 0,
                                      "total_cases": 6, "detail": "NameError: name 'x' is not defined", "outputs": []}]}}
    assert learner_safe(crash, PID)["curated"]["results"][0]["detail"] == "NameError: name 'x' is not defined"


@pytest.fixture
def captured_prompts(monkeypatch):
    prompts: list[str] = []
    feedback = AnalysisResult(mistakes=[], enhancements=[], watchouts=[], interview_tips=[],
                              overall_feedback="Compare your operator with the task.")

    async def draft(**kwargs):
        prompts.append(json.dumps(kwargs, default=str))
        return feedback

    class Model:
        def with_structured_output(self, *args):
            return self

        async def ainvoke(self, prompt):
            prompts.append(str(prompt))
            return feedback
    monkeypatch.setattr("app.services.deep_review.analyze_solution", draft)
    monkeypatch.setattr("app.services.deep_review.get_llm", lambda _: Model())
    monkeypatch.setattr("app.services.knowledge_base.get_vectorstore",
                        lambda: SimpleNamespace(similarity_search=lambda *a, **kw: []))
    return prompts


async def _learner(client, db, email):
    registered = (await client.post("/auth/register", json={"email": email, "password": "password123"})).json()
    db.add(Subscription(user_id=registered["user"]["id"], language="python",
                        expires_at=datetime.now(timezone.utc) + timedelta(days=42)))
    await db.commit()
    return {"Authorization": "Bearer " + registered["access_token"]}


def _assert_clean(text: str):
    for value in HIDDEN:
        assert value not in text, f"hidden test value {value!r} leaked"


async def test_practice_evaluation_never_exposes_hidden_values(client, db, captured_prompts):
    headers = await _learner(client, db, "privacy-practice@example.com")
    started = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": "p-start"},
                                json={"problem_id": PID, "language": "python"})
    sid = started.json()["session_id"]
    failed = await client.post(f"/practice/sessions/{sid}/actions", headers={**headers, "Idempotency-Key": "p-fail"},
                               json={"action": "submit", "code": WRONG})
    assert failed.status_code == 200, failed.text
    body = failed.json()
    assert body["outcome"] == "failed"
    result = body["evidence"]["curated"]["results"][0]
    assert result["outputs"] == [] and len(result["case_results"]) == result["total_cases"]
    assert body["tests"]["cases"] and body["tests"]["passed"] == result["passed_cases"]
    _assert_clean(failed.text)
    _assert_clean((await client.get(f"/practice/sessions/{sid}", headers=headers)).text)
    _assert_clean("\n".join(captured_prompts))
    assert captured_prompts, "the review prompts were not captured"


async def test_analyze_endpoint_never_exposes_hidden_values(client, db, captured_prompts):
    headers = await _learner(client, db, "privacy-analyze@example.com")
    response = await client.post("/analyze/", headers={**headers, "Idempotency-Key": "a-fail"},
                                 json={"problem_id": PID, "language": "python", "user_code": WRONG})
    assert response.status_code == 200, response.text
    assert response.json()["evidence"]["curated"]["results"][0]["status"] == "failed"
    _assert_clean(response.text)
    _assert_clean("\n".join(captured_prompts))


async def test_sessions_stored_before_the_fix_are_cleaned_when_read(client, db, monkeypatch):
    from app.routers.practice import render
    raw = {"problem_id": PID, "evidence": {"curated": {"results": [{
        "language": "python", "tier": 1, "status": "failed", "passed_cases": 0, "total_cases": 6,
        "detail": "case 5: got 2000, expected 1000000", "outputs": [7, 5, 9, 2, 2000, 13]}]}}}
    _assert_clean(json.dumps(render("sid", raw)))
