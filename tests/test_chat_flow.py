# Chat + analyze paid flows, with the LLM layer mocked so no network/API key
# is needed. Verifies: a successful chat debits exactly CHAT_COST and persists
# history; a provider failure refunds the debit; insufficient balance -> 402.
import pytest

from app.core.config import settings


async def _register(client, email="c@x.com", *, subscribe_user):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    await subscribe_user(r.json()["user"]["id"], 'python')
    return r.json()["access_token"]


async def test_chat_debits_and_persists(client, monkeypatch, subscribe_user):
    async def fake_rag(message, provider, history, language, **kwargs):
        return "Here is a hint."

    monkeypatch.setattr("app.routers.chat.run_rag_chat", fake_rag)
    token = await _register(client, subscribe_user=subscribe_user)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post("/chat/", headers=headers, json={"message": "hint for two sum?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "Here is a hint."
    assert body["peppercorns_remaining"] == 50 - settings.chat_cost
    thread_id = body["thread_id"]

    msgs = await client.get(f"/chat/threads/{thread_id}/messages", headers=headers)
    assert [m["role"] for m in msgs.json()] == ["user", "assistant"]


async def test_chat_refunds_on_provider_failure(client, monkeypatch, subscribe_user):
    async def boom(*a, **k):
        raise RuntimeError("provider down")

    monkeypatch.setattr("app.routers.chat.run_rag_chat", boom)
    token = await _register(client, "boom@x.com", subscribe_user=subscribe_user)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post("/chat/", headers=headers, json={"message": "hi"})
    assert r.status_code == 502

    me = await client.get("/auth/me", headers=headers)
    assert me.json()["peppercorns"] == 50  # debit was refunded


async def test_chat_insufficient_balance_returns_402(client, monkeypatch, subscribe_user):
    async def fake_rag(*a, **k):
        return "ok"

    monkeypatch.setattr("app.routers.chat.run_rag_chat", fake_rag)
    # New user with the bonus set to 0 for this test
    monkeypatch.setattr(settings, "signup_bonus", 0)
    token = await _register(client, "broke@x.com", subscribe_user=subscribe_user)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post("/chat/", headers=headers, json={"message": "hi"})
    assert r.status_code == 402


async def test_analyze_debits_five(client, monkeypatch, subscribe_user):
    from app.models.schemas import AnalysisResult

    # /analyze runs the precision pipeline (deep_review), which returns the
    # review plus the execution evidence behind it.
    async def fake_review(problem_id, user_code, language, provider):
        return AnalysisResult(
            mistakes=[], enhancements=[], watchouts=[], interview_tips=[],
            overall_feedback="Looks optimal.",
        ), {}

    monkeypatch.setattr("app.routers.analyze.deep_review", fake_review)
    token = await _register(client, "anlz@x.com", subscribe_user=subscribe_user)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/analyze/", headers=headers,
        json={"problem_id": "two-sum", "user_code": "def f(): pass", "language": "python"},
    )
    assert r.status_code == 200
    assert r.json()["peppercorns_remaining"] == 50 - settings.analyze_cost
