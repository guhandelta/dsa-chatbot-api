import asyncio

import pytest
from fastapi import HTTPException
from langchain_core.messages import HumanMessage
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import ChatMessage, InstructorLanguage, Transaction
from app.services.chat_model_routing import classify_question, run_routed_chat
from tests.test_language_access import account


class Unavailable(Exception):
    status_code = 503


@pytest.fixture(autouse=True)
def routing_config(monkeypatch):
    for field in ('google_api_key', 'openai_api_key', 'anthropic_api_key'):
        monkeypatch.setattr(settings, field, 'offline-test-key')
    monkeypatch.setattr(settings, 'default_provider', 'openai')
    monkeypatch.setattr(settings, 'chat_explain_provider', 'gemini')
    monkeypatch.setattr(settings, 'chat_code_provider', 'claude')
    monkeypatch.setattr(settings, 'chat_reasoning_provider', 'openai')


@pytest.mark.parametrize('question,task,provider', [
    ('Explain arrays', 'explain', 'gemini'),
    ('Debug this code: ```java\nint x = 1;```', 'code', 'claude'),
    ('Compare the time complexity of these approaches', 'reasoning', 'openai'),
])
async def test_question_routing(question, task, provider):
    calls = []
    async def generate(selected):
        calls.append(selected)
        return 'answer'
    answer, routing = await run_routed_chat(question, [], 'auto', generate)
    assert answer == 'answer' and calls == [provider]
    assert routing['task'] == task and not routing['fallback_used']
    assert classify_question('Why is that?', [HumanMessage(content=question)]) == task


async def test_skips_unconfigured_models_and_obeys_policy(monkeypatch):
    monkeypatch.setattr(settings, 'anthropic_api_key', '')
    calls = []
    async def generate(provider):
        calls.append(provider)
        return 'answer'
    await run_routed_chat('Debug my code', [], 'auto', generate)
    assert calls == ['openai']
    monkeypatch.setattr(settings, 'chat_code_provider', 'gemini')
    await run_routed_chat('Debug my code', [], 'auto', generate)
    assert calls[-1] == 'gemini'


async def test_timeout_fallback_is_bounded(monkeypatch):
    monkeypatch.setattr(settings, 'chat_model_timeout_seconds', 0.01)
    calls = []
    async def generate(provider):
        calls.append(provider)
        if provider == 'gemini':
            await asyncio.sleep(10)
        return 'fallback answer'
    answer, routing = await run_routed_chat('Explain arrays', [], 'auto', generate)
    assert answer == 'fallback answer' and calls == ['gemini', 'openai']
    assert routing['fallback_used'] and routing['provider'] == 'openai'


async def test_does_not_retry_application_rejections_or_cancellation():
    for failure in (HTTPException(403, 'Denied'), asyncio.CancelledError(), ValueError('Invalid result')):
        calls = []
        async def generate(provider):
            calls.append(provider)
            raise failure
        with pytest.raises(type(failure)):
            await run_routed_chat('Explain arrays', [], 'auto', generate)
        assert len(calls) == 1


async def test_no_configured_provider_makes_no_model_call(monkeypatch):
    for field in ('google_api_key', 'openai_api_key', 'anthropic_api_key'):
        monkeypatch.setattr(settings, field, '')
    async def generate(provider):
        pytest.fail('No model call should occur')
    with pytest.raises(HTTPException) as error:
        await run_routed_chat('Explain arrays', [], 'auto', generate)
    assert error.value.status_code == 503


async def test_student_provider_override_is_ignored_and_fallback_replays_once(client, db, monkeypatch):
    user, headers = await account(db, languages=('java',))
    headers['Idempotency-Key'] = 'automatic-once'
    calls = []
    async def generate(**kwargs):
        calls.append(kwargs['provider'])
        if kwargs['provider'] == 'gemini':
            raise Unavailable()
        return 'Explanation'
    monkeypatch.setattr('app.routers.chat.run_rag_chat', generate)
    body = {'message': 'Explain arrays', 'language': 'java', 'provider': 'claude'}
    first = await client.post('/chat/', headers=headers, json=body)
    assert first.status_code == 200, first.text
    assert first.json()['model_routing']['provider'] == 'openai'
    assert first.json()['model_routing']['fallback_used']
    again = await client.post('/chat/', headers=headers, json=body)
    assert again.json() == first.json() and calls == ['gemini', 'openai']
    assert first.json()['peppercorns_remaining'] == 50 - settings.chat_cost
    assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 2
    denied = await client.post('/chat/', headers={k: v for k, v in headers.items() if k != 'Idempotency-Key'},
                               json={**body, 'language': 'python'})
    assert denied.status_code == 403 and len(calls) == 2


async def test_exhausted_fallback_refunds_one_charge(client, db, monkeypatch):
    user, headers = await account(db, languages=('java',))
    calls = []
    async def generate(**kwargs):
        calls.append(kwargs['provider'])
        raise Unavailable()
    monkeypatch.setattr('app.routers.chat.run_rag_chat', generate)
    response = await client.post('/chat/', headers=headers, json={'message': 'Explain arrays', 'language': 'java'})
    assert response.status_code == 502 and calls == ['gemini', 'openai']
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == 50
    assert await db.scalar(select(func.count()).select_from(ChatMessage)) == 0
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.reason == 'refund:chat')) == 1


@pytest.mark.parametrize('role', ['admin', 'instructor'])
@pytest.mark.parametrize('provider', ['claude', None])
async def test_staff_manual_provider_is_preserved(client, db, monkeypatch, role, provider):
    user, headers = await account(db, role=role)
    if role == 'instructor':
        db.add(InstructorLanguage(user_id=user.id, language='java', assigned_by=user.id))
        await db.commit()
    calls = []
    async def generate(**kwargs):
        calls.append(kwargs['provider'])
        return 'Answer'
    monkeypatch.setattr('app.routers.chat.run_rag_chat', generate)
    body = {'message': 'Explain arrays', 'language': 'java'}
    if provider:
        body['provider'] = provider
    response = await client.post('/chat/', headers=headers, json=body)
    assert response.status_code == 200 and calls == [provider or 'gemini']
    assert response.json()['model_routing']['strategy'] == 'manual'


async def test_missing_configuration_does_not_charge(client, db, monkeypatch):
    _, headers = await account(db, languages=('java',))
    for field in ('google_api_key', 'openai_api_key', 'anthropic_api_key'):
        monkeypatch.setattr(settings, field, '')
    response = await client.post('/chat/', headers=headers, json={'message': 'Explain arrays', 'language': 'java'})
    assert response.status_code == 503
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == 50
    assert await db.scalar(select(func.count()).select_from(Transaction)) == 0
