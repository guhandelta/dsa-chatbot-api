"""Thread context is stable even when the learner's progress changes."""
from datetime import datetime, timezone

from app.db.models import ChatThread, LearningEvent, QuizSession
from tests.test_study_room import ask, model, register


async def test_auto_focus_stays_pinned_after_stage_completion(client, db, model):
    headers, uid = await register(client, db, "pinned-focus@example.com")
    first = (await client.post("/study/message", headers=headers, json=ask())).json()
    db.add(LearningEvent(user_id=uid, problem_id="python-path-01-values", language="python", kind="solved"))
    db.add(QuizSession(user_id=uid, language="python", node_id="python:stage-01", total=3,
                       answered=3, score=3, completed_at=datetime.now(timezone.utc)))
    await db.commit()
    follow = await client.post("/study/message", headers=headers, json=ask(thread_id=first["thread_id"]))
    assert follow.status_code == 200
    assert follow.json()["focus"]["id"] == "python:stage-01"
    changed = await client.post("/study/message", headers=headers, json=ask(
        thread_id=first["thread_id"], focus_id="python:stage-02"))
    assert changed.status_code == 409


async def test_comparison_thread_rejects_changing_second_language(client, db, model):
    headers, _ = await register(client, db, "compare-focus@example.com", ("python", "javascript", "java"))
    body = ask(mode="compare", compare_language="javascript")
    first = (await client.post("/study/message", headers=headers, json=body)).json()
    changed = await client.post("/study/message", headers=headers, json={
        **body, "thread_id": first["thread_id"], "compare_language": "java"})
    assert changed.status_code == 409


async def test_legacy_unpinned_threads_require_a_fresh_conversation(client, db, model):
    headers, uid = await register(client, db, "legacy-focus@example.com")
    legacy = ChatThread(user_id=uid, language="python", track="study-explain")
    db.add(legacy)
    await db.commit()
    response = await client.post("/study/message", headers=headers, json=ask(thread_id=legacy.id))
    assert response.status_code == 409 and "older conversation" in response.json()["detail"]
    assert not model.calls
