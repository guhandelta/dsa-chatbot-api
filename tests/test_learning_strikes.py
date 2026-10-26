"""Learning strikes: earned by failed paid evaluations, cleared by 2-3 related
questions, snowballing on wrong answers up to the cap; extra practice on demand."""
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import ChallengeSet, LearningStrike, Subscription, WorkspaceRun
from app.models.schemas import AnalysisResult
from app.services import learning_strikes, quiz

PID = "python-path-01-values"
NODE = "python:stage-01"
WRONG = "def total_cost(price, quantity):\n    return price + quantity\n"


@pytest.fixture
def reviewer(monkeypatch):
    feedback = AnalysisResult(mistakes=[], enhancements=[], watchouts=[], interview_tips=[],
                              overall_feedback="Compare the operator with the task.")

    async def draft(**kwargs):
        return feedback

    class Model:
        def with_structured_output(self, *args):
            return self

        async def ainvoke(self, prompt):
            return feedback
    monkeypatch.setattr("app.services.deep_review.analyze_solution", draft)
    monkeypatch.setattr("app.services.deep_review.get_llm", lambda _: Model())
    monkeypatch.setattr("app.services.knowledge_base.get_vectorstore",
                        lambda: SimpleNamespace(similarity_search=lambda *a, **kw: []))


async def _learner(client, db, email="strikes@example.com"):
    registered = (await client.post("/auth/register", json={"email": email, "password": "password123"})).json()
    uid = registered["user"]["id"]
    db.add(Subscription(user_id=uid, language="python", expires_at=datetime.now(timezone.utc) + timedelta(days=42)))
    await db.commit()
    return uid, {"Authorization": "Bearer " + registered["access_token"]}


async def _fail_evaluation(client, headers, key="fail"):
    started = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": f"start-{key}"},
                                json={"problem_id": PID, "language": "python"})
    assert started.status_code == 200, started.text
    response = await client.post(f"/practice/sessions/{started.json()['session_id']}/actions",
                                 headers={**headers, "Idempotency-Key": key}, json={"action": "submit", "code": WRONG})
    assert response.status_code == 200, response.text
    return response.json()


def _right(item: dict):
    if item["type"] in ("mcq", "mcq_code"):
        return item["answer"]
    return item["solution"]


def _wrong(item: dict):
    if item["type"] in ("mcq", "mcq_code"):
        return (item["answer"] + 1) % len(item["choices"])
    return "def nothing():\n    pass\n"


def test_topic_and_question_pool_come_from_the_path_stage():
    assert learning_strikes.topic_node("python", PID) == NODE
    assert learning_strikes.topic_node("python", "missing-number") == NODE  # stage 1 practice set
    pool = learning_strikes.candidates("python", NODE, PID)
    assert pool and {i["type"] for i in pool} <= {"mcq", "mcq_code", "write_snippet", "fix_bug"}


def test_pick_mixes_formats_and_prefers_unseen_items():
    pool = learning_strikes.candidates("python", NODE, PID)
    chosen = learning_strikes.pick(pool, 3, ["debug", "mcq", "coding"], set(), "seed")
    formats = [learning_strikes.FORMAT_OF[i["type"]] for i in chosen]
    assert len(chosen) == 3 and len(set(formats)) >= 2
    seen = {i["id"] for i in pool[:-1]}
    again = learning_strikes.pick(pool, 1, ["mcq", "coding", "debug"], seen, "seed")
    assert again[0]["id"] not in seen or len(pool) == 1


async def test_failed_evaluation_earns_a_strike_with_where_details(client, db, reviewer):
    uid, headers = await _learner(client, db)
    body = await _fail_evaluation(client, headers)
    strike = body["strike"]
    assert strike["where"]["stage"] == "evaluation" and strike["where"]["phase"] == "wrong_answer"
    assert strike["where"]["total"] == 6 and strike["where"]["passed"] < 6
    assert strike["set"]["required"] in (2, 3) and len(strike["set"]["questions"]) >= strike["set"]["required"]
    question = strike["set"]["questions"][0]
    assert "answer" not in question and "solution" not in question and "tests" not in question
    assert body["solution_available"] is False
    # Free test runs never earn strikes.
    run = await client.post(f"/workspace/{PID}/run", headers=headers, json={
        "language": "python", "entry": "solution.py", "files": [{"name": "solution.py", "content": WRONG}]})
    assert run.status_code == 200
    assert await db.scalar(select(func.count()).select_from(LearningStrike).where(LearningStrike.user_id == uid)) == 1


async def test_strikes_gate_new_challenges_but_not_a_retry(client, db, reviewer):
    uid, headers = await _learner(client, db)
    await _fail_evaluation(client, headers)
    retry = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": "retry"},
                              json={"problem_id": PID, "language": "python"})
    assert retry.status_code == 200
    other = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": "other"},
                              json={"problem_id": "python-path-02-conditions", "language": "python"})
    assert other.status_code == 409 and other.json()["detail"]["open_strikes"] == 1
    overview = (await client.get("/strikes", params={"language": "python"}, headers=headers)).json()
    assert overview["blocking"] is True and overview["cap"] == settings.learning_strike_cap
    from app.services.learning_path import progress
    node = next(n for n in (await progress(db, uid, "python"))["nodes"] if n["id"] == NODE)
    assert node["open_strikes"] is True and node["complete"] is False


async def test_correct_answers_clear_the_strike_and_unblock(client, db, reviewer):
    uid, headers = await _learner(client, db)
    strike = (await _fail_evaluation(client, headers))["strike"]
    bank = quiz.items("python")
    item_set = strike["set"]
    for question in item_set["questions"][: item_set["required"]]:
        result = await client.post(f"/strikes/sets/{item_set['id']}/answers", headers=headers,
                                   json={"item_id": question["id"], "response": _right(bank[question["id"]])})
        assert result.status_code == 200, result.text
        assert result.json()["correct"] is True
        if question["format"] != "mcq":
            assert "expected" not in result.json()  # reference code stays hidden
    assert result.json()["cleared"] is True
    stored = await db.scalar(select(LearningStrike).where(LearningStrike.id == strike["id"]))
    await db.refresh(stored)
    assert stored.status == "cleared"
    other = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": "next"},
                              json={"problem_id": "python-path-02-conditions", "language": "python"})
    assert other.status_code == 200, other.text


async def test_wrong_answers_snowball_up_to_the_cap_then_step_back(client, db, reviewer, monkeypatch):
    monkeypatch.setattr(settings, "learning_strike_cap", 2)
    uid, headers = await _learner(client, db)
    strike = (await _fail_evaluation(client, headers))["strike"]
    bank = quiz.items("python")
    item_set = strike["set"]
    first = item_set["questions"][0]
    missed = (await client.post(f"/strikes/sets/{item_set['id']}/answers", headers=headers,
                                json={"item_id": first["id"], "response": _wrong(bank[first["id"]])})).json()
    assert missed["correct"] is False and missed["new_strike"]["source"] == "challenge"
    assert missed["new_strike"]["where"]["item_id"] == first["id"]
    assert missed["replacement"] and missed["replacement"]["id"] != first["id"]
    assert len(missed["set"]["questions"]) == len(item_set["questions"]) + 1
    second = missed["set"]["questions"][1]
    capped = (await client.post(f"/strikes/sets/{item_set['id']}/answers", headers=headers,
                                json={"item_id": second["id"], "response": _wrong(bank[second["id"]])})).json()
    assert capped["new_strike"] is None and capped["cap_reached"]["action"] == "mentor_step_back"
    assert await db.scalar(select(func.count()).select_from(LearningStrike).where(
        LearningStrike.user_id == uid, LearningStrike.status == "open")) == 2
    again = await client.post(f"/strikes/sets/{item_set['id']}/answers", headers=headers,
                              json={"item_id": first["id"], "response": _right(bank[first["id"]])})
    assert again.status_code == 409  # one answer per question


async def test_extra_practice_is_open_anytime_and_capped_monthly(client, db, monkeypatch):
    monkeypatch.setattr(settings, "extra_practice_sets_per_month", 1)
    uid, headers = await _learner(client, db)
    extra = await client.post("/strikes/practice", headers=headers,
                              json={"language": "python", "problem_id": PID, "count": 3})
    assert extra.status_code == 200, extra.text
    view = extra.json()
    assert view["kind"] == "extra" and len(view["questions"]) == 3
    bank = quiz.items("python")
    question = view["questions"][0]
    wrong = await client.post(f"/strikes/sets/{view['id']}/answers", headers=headers,
                              json={"item_id": question["id"], "response": _wrong(bank[question["id"]])})
    assert wrong.json()["new_strike"] is None  # extra practice never earns strikes
    assert (await client.post("/strikes/practice", headers=headers,
                              json={"language": "python", "problem_id": PID})).status_code == 429
    overview = (await client.get("/strikes", params={"language": "python"}, headers=headers)).json()
    assert overview["extra_practice"]["remaining_this_month"] == 0
    assert overview["extra_practice"]["answered"] == 1 and overview["open"] == []


async def test_challenge_sets_are_private_and_exported(client, db, reviewer):
    uid, headers = await _learner(client, db)
    strike = (await _fail_evaluation(client, headers))["strike"]
    _, other = await _learner(client, db, email="strikes-other@example.com")
    assert (await client.get(f"/strikes/sets/{strike['set']['id']}", headers=other)).status_code == 404
    exported = (await client.get("/mentor/profile/export", headers=headers)).json()
    assert exported["strikes"]["strikes"][0]["where"]["stage"] == "evaluation"


async def test_a_strike_whose_questions_run_out_moves_to_a_new_set(client, db, reviewer, monkeypatch):
    uid, headers = await _learner(client, db)
    strike = (await _fail_evaluation(client, headers))["strike"]
    item_set = strike["set"]
    bank = quiz.items("python")
    # Only the questions already in the set exist for this topic.
    in_set = [bank[q["id"]] for q in item_set["questions"]]
    monkeypatch.setattr(learning_strikes, "candidates", lambda *a: in_set)
    monkeypatch.setattr(settings, "learning_strike_cap", 1)
    first = item_set["questions"][0]
    missed = (await client.post(f"/strikes/sets/{item_set['id']}/answers", headers=headers,
                                json={"item_id": first["id"], "response": _wrong(bank[first["id"]])})).json()
    assert len(in_set) == item_set["required"]  # one miss makes this set impossible
    assert missed["renewed_set"]["id"] != item_set["id"]
    overview = (await client.get("/strikes", params={"language": "python"}, headers=headers)).json()
    assert overview["open"][0]["set"]["id"] == missed["renewed_set"]["id"]
    assert overview["open"][0]["set"]["complete"] is False


async def test_a_snowballed_strike_avoids_questions_waiting_in_other_sets(client, db, reviewer):
    uid, headers = await _learner(client, db)
    strike = (await _fail_evaluation(client, headers))["strike"]
    bank = quiz.items("python")
    first = strike["set"]["questions"][0]
    missed = (await client.post(f"/strikes/sets/{strike['set']['id']}/answers", headers=headers,
                                json={"item_id": first["id"], "response": _wrong(bank[first["id"]])})).json()
    waiting = {q["id"] for q in missed["set"]["questions"]}
    fresh = {q["id"] for q in missed["new_strike"]["set"]["questions"]}
    pool = learning_strikes.candidates("python", NODE, PID)
    if len(pool) - len(waiting) >= len(fresh):
        assert not fresh & waiting
