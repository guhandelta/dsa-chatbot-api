import asyncio
import pytest
from sqlalchemy import select,func,update
from app.core.config import settings
from app.db.models import User,ChatThread,ChatMessage,KnowledgeDocument,Transaction
from app.services import agentic_rag as ar
from app.services.entitlements import grant
from tests.test_agentic_rag import Scripted,SEARCH,ANSWER,doc


async def register(client,db,role='admin',email='pilot@example.com'):
    response=(await client.post('/auth/register',json={'email':email,'password':'password123'})).json()
    uid=response['user']['id']
    await db.execute(update(User).where(User.id==uid).values(role=role))
    if role == 'student':
        await grant(db, uid, 'java', days=42)
    await db.commit()
    return {'Authorization':'Bearer '+response['access_token']},uid


@pytest.mark.parametrize('enabled,role',[(False,'admin'),(True,'student'),(True,'instructor')])
async def test_private_pilot_gate_precedes_debit(client,db,monkeypatch,enabled,role):
    monkeypatch.setattr(settings,'agentic_rag_enabled',enabled)
    headers,uid=await register(client,db,role)
    response=await client.post('/chat/',headers=headers,json={'message':'arrays','language':'java','retrieval_mode':'agentic'})
    assert response.status_code==403
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert (await client.get('/chat/capabilities',headers=headers)).json()['agentic_retrieval'] is False


async def test_agentic_api_replay_and_mode_conflict(client,db,monkeypatch):
    monkeypatch.setattr(settings,'agentic_rag_enabled',True)
    headers,uid=await register(client,db)
    model=Scripted([SEARCH,{'action':'answer'},ANSWER])
    monkeypatch.setattr(ar,'bounded_model',model.factory)
    monkeypatch.setattr('app.services.curriculum_search.search',lambda *a,**kw:[doc()])
    headers['Idempotency-Key']='pilot-once'
    body={'message':'arrays','language':'java','track':'language','retrieval_mode':'agentic'}
    first=await client.post('/chat/',headers=headers,json=body)
    assert first.status_code==200,first.text
    assert first.json()['retrieval']['strategy']=='agentic'
    assert first.json()['sources'][0]['filename']=='Java arrays.md'
    again=await client.post('/chat/',headers=headers,json=body)
    assert first.json()==again.json() and len(model.calls)==3
    assert (await client.post('/chat/',headers=headers,json={**body,'retrieval_mode':'standard'})).status_code==409
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus-settings.chat_cost
    assert await db.scalar(select(func.count()).select_from(ChatMessage))==2


async def test_provider_failure_refunds_and_persists_no_thread(client,db,monkeypatch):
    monkeypatch.setattr(settings,'agentic_rag_enabled',True)
    headers,uid=await register(client,db)
    monkeypatch.setattr(ar,'bounded_model',Scripted([RuntimeError('SECRET')]).factory)
    response=await client.post('/chat/',headers=headers,json={'message':'arrays','language':'java','retrieval_mode':'agentic'})
    assert response.status_code==502 and 'SECRET' not in response.text
    assert await db.scalar(select(func.count()).select_from(ChatThread))==0
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.reason=='refund:chat'))==1


async def test_foreign_thread_and_oversized_input_do_not_charge(client,db,monkeypatch):
    monkeypatch.setattr(settings,'agentic_rag_enabled',True)
    owner,other=await register(client,db,email='owner@example.com')
    headers,uid=await register(client,db,email='second@example.com')
    thread=ChatThread(user_id=other,title='Private')
    db.add(thread);await db.commit()
    body={'message':'arrays','language':'java','retrieval_mode':'agentic','thread_id':thread.id}
    assert (await client.post('/chat/',headers=headers,json=body)).status_code==404
    assert (await client.post('/chat/',headers=headers,json={**body,'thread_id':None,'message':'界'*2001})).status_code==422
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus


async def test_standard_path_remains_default_and_no_thread_write_during_model(client,db,monkeypatch):
    headers,uid=await register(client,db,role='student')
    async def ordinary(**kwargs):
        assert await db.scalar(select(func.count()).select_from(ChatThread))==0
        return 'Ordinary RAG'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',ordinary)
    response=await client.post('/chat/',headers=headers,json={'message':'arrays','language':'java'})
    assert response.status_code==200 and response.json()['retrieval'] is None
    assert response.json()['answer']=='Ordinary RAG'


async def test_approved_upload_tools_drop_revoked_changed_and_focused_sources(db):
    user=User(email='source-owner@example.com',hashed_password='unused');db.add(user);await db.flush()
    row=KnowledgeDocument(owner_id=user.id,filename='Java arrays.pdf',language='java',track='language',status='published',text='Java arrays are fixed length.')
    db.add(row);await db.commit()
    tools=ar.ReadOnlyTools(db,ar.Scope('java','language'))
    docs=await tools.search('uploads','arrays')
    assert docs and await tools.reauthorize(docs)==docs
    row.text='Changed approved source.';await db.commit()
    assert not await tools.reauthorize(docs)
    row.text='Java arrays are fixed length.';row.status='rejected';await db.commit()
    assert not await tools.search('uploads','arrays')
    row.status='published';await db.commit()
    assert not await ar.ReadOnlyTools(db,ar.Scope('java','language',focus_id='two-sum')).search('uploads','arrays')
    with pytest.raises(ValueError,match='Unknown'):await tools.search('shell','whoami')


async def test_slow_chat_does_not_hold_sqlite_write_lock(tmp_path,monkeypatch):
    from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
    from httpx import AsyncClient,ASGITransport
    from app.db.database import Base,get_session
    from app.main import app
    engine=create_async_engine('sqlite+aiosqlite:///'+str(tmp_path/'lock.db'),connect_args={'timeout':.1})
    async with engine.begin() as c:await c.run_sync(Base.metadata.create_all)
    factory=async_sessionmaker(engine,expire_on_commit=False)
    async def dependency():
        async with factory() as session:yield session
    app.dependency_overrides[get_session]=dependency
    entered,release=asyncio.Event(),asyncio.Event()
    async def slow(**kwargs):
        entered.set();await release.wait();return 'A question?'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',slow)
    task=None
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
            result=(await client.post('/auth/register',json={'email':'slow@example.com','password':'password123'})).json()
            async with factory() as session:
                await grant(session, result['user']['id'], 'java', days=42)
                await session.commit()
            headers={'Authorization':'Bearer '+result['access_token']}
            task=asyncio.create_task(client.post('/chat/',headers=headers,json={'message':'arrays','language':'java'}))
            await asyncio.wait_for(entered.wait(),3)
            other=await asyncio.wait_for(client.post('/auth/register',json={'email':'unblocked@example.com','password':'password123'}),2)
            assert other.status_code==201,other.text
            release.set()
            assert (await task).status_code==200
    finally:
        release.set()
        if task is not None and not task.done():await task
        app.dependency_overrides.pop(get_session,None)
        await engine.dispose()


@pytest.mark.parametrize('answer',[{'answer':'Unsupported claim','source_ids':['S999']},'{"answer":"truncated'])
async def test_invalid_final_answer_refunds_once_and_replays_failure(client,db,monkeypatch,answer):
    monkeypatch.setattr(settings,'agentic_rag_enabled',True)
    headers,uid=await register(client,db)
    model=Scripted([SEARCH,{'action':'answer'},answer])
    monkeypatch.setattr(ar,'bounded_model',model.factory)
    monkeypatch.setattr('app.services.curriculum_search.search',lambda *a,**kw:[doc()])
    headers['Idempotency-Key']='invalid-answer'
    payload={'message':'arrays','language':'java','track':'language','retrieval_mode':'agentic'}
    first=await client.post('/chat/',headers=headers,json=payload)
    repeat=await client.post('/chat/',headers=headers,json=payload)
    assert first.status_code==repeat.status_code==502
    assert len(model.calls)==3
    assert await db.scalar(select(func.count()).select_from(ChatMessage))==0
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.reason=='refund:chat'))==1


async def test_external_revocation_during_generation_refunds_and_withholds_answer(client,db,session_factory,monkeypatch):
    monkeypatch.setattr(settings,'agentic_rag_enabled',True)
    headers,uid=await register(client,db)
    row=KnowledgeDocument(owner_id=uid,filename='Java arrays.pdf',language='java',track='language',status='published',text='Java arrays are fixed length.')
    db.add(row);await db.commit();doc_id=row.id
    class Revoking(Scripted):
        async def ainvoke(self,messages):
            if len(self.calls)==3:
                async with session_factory() as other:
                    await other.execute(update(KnowledgeDocument).where(KnowledgeDocument.id==doc_id).values(status='rejected'))
                    await other.commit()
            return await super().ainvoke(messages)
    model=Revoking([{'action':'search','tool':'uploads','query':'arrays'},{'action':'answer'},ANSWER])
    monkeypatch.setattr(ar,'bounded_model',model.factory)
    response=await client.post('/chat/',headers=headers,json={'message':'arrays','language':'java','track':'language','retrieval_mode':'agentic'})
    assert response.status_code==502 and ANSWER['answer'] not in response.text
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(ChatMessage))==0
