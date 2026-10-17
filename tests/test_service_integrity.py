import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime,timedelta,timezone
import pytest
from sqlalchemy import select,func
from app.db.models import ServiceOperation,Transaction,LearningEvent,User,Subscription
from app.models.schemas import AnalysisResult
from app.core.config import settings
from app.services import entitlements


async def register(client,email='integrity@example.com'):
    body=(await client.post('/auth/register',json={'email':email,'password':'password123'})).json()
    return {'Authorization':'Bearer '+body['access_token']},body['user']['id']


async def test_chat_receipt_replays_without_charging_and_rejects_changed_body(client,monkeypatch,db):
    calls=[]
    async def reply(**kw):calls.append(kw);return 'Grounded answer'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    headers,uid=await register(client);headers['Idempotency-Key']='same-request'
    first=await client.post('/chat/',headers=headers,json={'message':'Help'})
    again=await client.post('/chat/',headers=headers,json={'message':'Help'})
    assert first.status_code==again.status_code==200
    assert first.json()==again.json() and len(calls)==1
    assert (await client.post('/chat/',headers=headers,json={'message':'Different'})).status_code==409
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.user_id==uid,Transaction.reason=='chat'))==1


async def test_failed_operation_refunds_once_and_replays_error(client,monkeypatch,db):
    calls=[]
    async def fail(**kw):calls.append(kw);raise RuntimeError('infrastructure')
    monkeypatch.setattr('app.routers.chat.run_rag_chat',fail)
    headers,uid=await register(client);headers['Idempotency-Key']='failed-request'
    for _ in range(2):assert (await client.post('/chat/',headers=headers,json={'message':'help'})).status_code==502
    assert len(calls)==1
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.user_id==uid,Transaction.reason=='refund:chat'))==1


async def test_suspended_chat_and_rate_limit_do_not_charge(client,monkeypatch,db):
    headers,uid=await register(client)
    user=await db.get(User,uid);user.status='suspended';await db.commit()
    assert (await client.post('/chat/',headers=headers,json={'message':'hi'})).status_code==403
    user.status='active';await db.commit()
    monkeypatch.setattr(settings,'chats_per_hour',1)
    async def reply(**kw):return 'reply'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    assert (await client.post('/chat/',headers=headers,json={'message':'hi'})).status_code==200
    assert (await client.post('/chat/',headers=headers,json={'message':'again'})).status_code==429


async def test_reflection_requires_verified_solve_and_never_creates_solve(client,db):
    headers,uid=await register(client)
    params={'problem_id':'two-sum','language':'java','reasoning':'I used complements.'}
    assert (await client.post('/mentor/reflect',headers=headers,params=params)).status_code==403
    db.add(LearningEvent(user_id=uid,problem_id='two-sum',language='java',kind='solved'));await db.commit()
    for _ in range(2):assert (await client.post('/mentor/reflect',headers=headers,params=params)).status_code==200
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id==uid,LearningEvent.kind=='solved'))==1
    params['language']='javascript'
    assert (await client.post('/mentor/reflect',headers=headers,params=params)).status_code==403


def signed(payload,secret='whsec_test',stamp=None):
    raw=json.dumps(payload,separators=(',',':')).encode();stamp=stamp or int(time.time())
    sig=hmac.new(secret.encode(),str(stamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    return raw,{'Stripe-Signature':f't={stamp},v1={sig}','Content-Type':'application/json'}


async def test_subscription_signature_idempotency_and_cancelled_access(client,db,monkeypatch):
    headers,uid=await register(client)
    monkeypatch.setattr(settings,'stripe_webhook_secret','whsec_test')
    end=int(time.time())+86400
    payload={'id':'evt_one','type':'customer.subscription.created','data':{'object':{'id':'sub_one','status':'active','current_period_end':end,'metadata':{'user_id':uid,'language':'java'}}}}
    raw,signature=signed(payload)
    assert (await client.post('/subscriptions/webhook',content=raw,headers={'Stripe-Signature':'nonsense'})).status_code==400
    assert (await client.post('/subscriptions/webhook',content=raw,headers=signature)).status_code==200
    assert (await client.post('/subscriptions/webhook',content=raw,headers=signature)).json()=={'duplicate':True}
    assert len(await entitlements.list_for(db,uid))==1
    payload['id']='evt_two';payload['type']='customer.subscription.deleted';payload['data']['object']['status']='canceled'
    raw,signature=signed(payload)
    assert (await client.post('/subscriptions/webhook',content=raw,headers=signature)).status_code==200
    assert (await entitlements.check(db,uid,'java'))['entitled']
    db.expire_all()
    sub=await db.scalar(select(Subscription).where(Subscription.provider_ref=='sub_one'))
    sub.expires_at=datetime.now(timezone.utc)-timedelta(seconds=1);await db.commit()
    assert not (await entitlements.check(db,uid,'java'))['entitled']
    raw,signature=signed(payload,stamp=int(time.time())-600)
    assert (await client.post('/subscriptions/webhook',content=raw,headers=signature)).status_code==400


async def test_langgraph_session_survives_new_requests_and_replays_actions(client,monkeypatch,db):
    from app.graphs.practice import PracticeDeps
    calls=[]
    async def notes(*a):return ['notes']
    async def review(*a):
        calls.append(a)
        return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Passed').model_dump(),{'curated':{'results':[{'language':'java','tier':1,'status':'passed','total_cases':6,'passed_cases':6}]}}
    async def hint(**kw):return 'What invariant holds?'
    monkeypatch.setattr('app.routers.practice.default_deps',lambda:PracticeDeps(notes,lambda *a:(True,''),review,hint,lambda p:None))
    headers,uid=await register(client)
    start=await client.post('/practice/sessions',headers=headers,json={'problem_id':'java-path-01-values','language':'java'})
    assert start.status_code==200,start.text
    sid=start.json()['session_id']
    assert start.json()['awaiting']=='learner'
    read=await client.get('/practice/sessions/'+sid,headers=headers)
    assert read.json()['awaiting']=='learner',read.text
    headers['Idempotency-Key']='submit-one'
    action={'action':'submit','code':'public int totalCost(int a, int b){return a*b;}'}
    first=await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=action)
    assert first.status_code==200,first.text
    assert first.json()['awaiting']=='reflection' and first.json()['solution_available']
    again=await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=action)
    assert first.json()==again.json() and len(calls)==1
    fresh=await client.get('/practice/sessions/'+sid,headers=headers)
    assert fresh.json()['awaiting']=='reflection'
    headers['Idempotency-Key']='reflect-one'
    reflected=await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json={'action':'reflect','reasoning':'Multiplication models repeated equal amounts.'})
    assert reflected.status_code==200,reflected.text
    assert reflected.json()['awaiting'] is None
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id==uid,LearningEvent.kind=='solved'))==1
    other,_=await register(client,'another@example.com')
    assert (await client.get('/practice/sessions/'+sid,headers=other)).status_code==404


async def test_inflight_duplicate_is_rejected_without_second_work(client,monkeypatch):
    entered=asyncio.Event();release=asyncio.Event();calls=[]
    async def reply(**kw):
        calls.append(kw);entered.set();await release.wait();return 'reply'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    headers,_=await register(client);headers['Idempotency-Key']='inflight'
    task=asyncio.create_task(client.post('/chat/',headers=headers,json={'message':'hi'}))
    await asyncio.wait_for(entered.wait(),5)
    duplicate=await client.post('/chat/',headers=headers,json={'message':'hi'})
    assert duplicate.status_code==409
    release.set()
    assert (await task).status_code==200
    assert len(calls)==1


async def test_blocked_retry_adds_only_one_strike(client,db):
    headers,uid=await register(client);headers['Idempotency-Key']='blocked'
    payload={'problem_id':'two-sum','language':'python','user_code':'import os\nos.system("anything")'}
    for _ in range(2):assert (await client.post('/analyze/',headers=headers,json=payload)).status_code==400
    db.expire_all()
    assert (await db.get(User,uid)).strikes==1


def test_python_screen_resolves_import_alias_and_ignores_comments():
    from app.services.code_screener import screen
    assert screen('from os import system as harmless\nharmless("x")','python').verdict=='block'
    assert screen('# import subprocess\ndef f(x): return x','python').allowed


async def test_expired_interrupted_request_refunds_once(client,db):
    from app.services.peppercorns import debit
    headers,uid=await register(client);key='interrupted';headers['Idempotency-Key']=key
    from app.models.schemas import ChatRequest
    payload=ChatRequest(message='hi').model_dump()
    opid=hashlib.sha256(json.dumps([uid,'chat',key]).encode()).hexdigest()
    fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    await debit(db,uid,settings.chat_cost,'chat')
    db.add(ServiceOperation(id=opid,user_id=uid,scope='chat',fingerprint=fingerprint,amount=settings.chat_cost,reason='chat',created_at=datetime.now(timezone.utc)-timedelta(hours=1)))
    await db.commit()
    for _ in range(2):assert (await client.post('/chat/',headers=headers,json={'message':'hi'})).status_code==503
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus


async def test_mentor_lookup_failure_after_debit_is_refunded(client,db,monkeypatch):
    headers,uid=await register(client)
    await entitlements.grant(db,uid,'java');await db.commit()
    async def broken(*a,**kw):raise RuntimeError('profile database lookup failed')
    monkeypatch.setattr('app.routers.mentor._current_tier',broken)
    result=await client.post('/mentor/ask',headers=headers,json={'problem_id':'two-sum','language':'java','reasoning':'I am considering a map'})
    assert result.status_code==502
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus


async def test_final_learning_write_failure_rolls_back_and_refunds(client,db,monkeypatch):
    headers,uid=await register(client)
    async def review(**kw):return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Feedback'),{}
    async def broken(*a,**kw):raise RuntimeError('learning write failed')
    monkeypatch.setattr('app.routers.analyze.deep_review',review)
    monkeypatch.setattr('app.routers.analyze.save_evaluation',broken)
    result=await client.post('/analyze/',headers=headers,json={'problem_id':'two-sum','language':'java','user_code':'public int[] twoSum(int[] a,int t){return new int[]{0,1};}'})
    assert result.status_code==502
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id==uid))==0


async def test_published_problem_retains_executable_tests_and_refreshes_catalog(tmp_path,monkeypatch):
    from app.services import training,training_pipeline,content_catalog,problem_catalog
    from app.services.deep_review import gather_evidence
    from app.services.curriculum_search import _index
    cases=[training.TestCase(args=[x],expected=x*2) for x in (0,1,-1,2,10,100)]
    problem=training.EnrichedProblem(title='Double value',difficulty='Easy',category='Arithmetic',statement='Return twice the input.',examples=['2 -> 4'],hints=['Consider arithmetic.'],approach='Multiply by two.',thinking_style=[],edge_cases=[],interview_tips=[],test_cases=cases,solutions=[training.SolutionOut(language='javascript',function_name='doubleValue',code='function doubleValue(x){return x*2;}',explanation='Double the input.',was_supplied=False), training.SolutionOut(language='java',function_name='doubleValue',code='public int doubleValue(int x){return x*2;}',explanation='Double the input.',was_supplied=False)])
    async def enrich(*a):return problem
    monkeypatch.setattr(training,'enrich_problem',enrich)
    monkeypatch.setattr(training_pipeline,'upsert_problem',lambda *a:1)
    monkeypatch.setattr(training_pipeline,'PROBLEMS_DIR',tmp_path)
    monkeypatch.setattr(content_catalog,'LEGACY_DIR',tmp_path)
    monkeypatch.setattr(problem_catalog,'PROBLEMS_DIR',tmp_path)
    content_catalog.list_content.cache_clear();problem_catalog.list_problems.cache_clear();_index.cache_clear()
    try:
        assert not any(c.id=='double-value' for c in content_catalog.list_content())
        result=await training_pipeline.run_pipeline('double-value','Double it',{},'openai')
        assert result['status']=='published'
        args,expected,names,_=content_catalog.load_test_cases('double-value')
        assert len(args)==len(expected)==6 and names['javascript']=='doubleValue'
        assert any(c.id=='double-value' and c.has_tests for c in content_catalog.list_content())
        evidence=await gather_evidence('double-value','function doubleValue(x){return x*2;}','javascript')
        assert evidence['curated']['results'][0]['passed_cases']==6
    finally:
        content_catalog.list_content.cache_clear();problem_catalog.list_problems.cache_clear();_index.cache_clear()


async def test_stale_subscription_update_cannot_undo_cancellation(client,db,monkeypatch):
    _,uid=await register(client)
    monkeypatch.setattr(settings,'stripe_webhook_secret','whsec_test')
    now=int(time.time());end=now+86400
    base={'status':'active','id':'sub_order','current_period_end':end,'metadata':{'user_id':uid,'language':'java'}}
    events=[('created',now,{}),('updated',now+2,{'cancel_at_period_end':True}),('updated',now+1,{'cancel_at_period_end':False})]
    for i,(kind,created,fields) in enumerate(events):
        payload={'id':f'evt_order_{i}','created':created,'type':'customer.subscription.'+kind,'data':{'object':{**base,**fields}}}
        raw,headers=signed(payload)
        assert (await client.post('/subscriptions/webhook',content=raw,headers=headers)).status_code==200
    sub=await db.scalar(select(Subscription).where(Subscription.provider_ref=='sub_order'))
    assert sub.status=='cancelled'


async def test_recovery_settles_expired_reservation_without_duplicate_credit(client,db):
    from app.services.operations import recover_expired_scope
    from app.services.peppercorns import debit
    from app.db.models import PracticeSession
    _,uid=await register(client)
    item=PracticeSession(user_id=uid,problem_id='two-sum',language='java',provider='gemini',busy=True,busy_token='a'*64)
    db.add(item);await db.flush();sid=item.id
    await debit(db,uid,settings.analyze_cost,'analyze')
    db.add(ServiceOperation(id='a'*64,user_id=uid,scope='practice:'+sid,fingerprint='b'*64,amount=settings.analyze_cost,reason='analyze',created_at=datetime.now(timezone.utc)-timedelta(hours=1)))
    await db.commit()
    assert await recover_expired_scope(db,uid,'practice:'+sid)
    assert not await recover_expired_scope(db,uid,'practice:'+sid)
    db.expire_all()
    assert not (await db.get(PracticeSession,sid)).busy
    assert (await db.get(User,uid)).peppercorns==settings.signup_bonus


async def test_admin_grant_receipt_prevents_double_extension(client,db):
    headers,uid=await register(client)
    user=await db.get(User,uid);user.role='admin';await db.commit()
    headers['Idempotency-Key']='manual-grant'
    params={'user_id':uid,'language':'java','days':30}
    first=await client.post('/subscriptions/admin/grant',headers=headers,params=params)
    again=await client.post('/subscriptions/admin/grant',headers=headers,params=params)
    assert first.status_code==again.status_code==200
    assert first.json()==again.json()
    assert len(await entitlements.list_for(db,uid))==1


async def test_concurrent_graph_action_cannot_release_the_active_lock(client,monkeypatch,db):
    from app.graphs.practice import PracticeDeps
    from app.db.models import PracticeSession
    entered=asyncio.Event();release=asyncio.Event()
    async def notes(*a):return []
    async def review(*a):
        entered.set();await release.wait()
        return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Reviewed').model_dump(),{}
    async def hint(**kw):return 'Question'
    monkeypatch.setattr('app.routers.practice.default_deps',lambda:PracticeDeps(notes,lambda *a:(True,''),review,hint,lambda p:None))
    headers,_=await register(client)
    sid=(await client.post('/practice/sessions',headers=headers,json={'problem_id':'two-sum','language':'java'})).json()['session_id']
    headers['Idempotency-Key']='first-action'
    body={'action':'submit','code':'public int[] twoSum(int[] a,int t){return new int[]{0,1};}'}
    first=asyncio.create_task(client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=body))
    await asyncio.wait_for(entered.wait(),5)
    other={**headers,'Idempotency-Key':'second-action'}
    rejected=await client.post(f'/practice/sessions/{sid}/actions',headers=other,json=body)
    assert rejected.status_code==409,rejected.text
    db.expire_all()
    assert (await db.get(PracticeSession,sid)).busy
    release.set()
    assert (await first).status_code==200


async def test_graph_failure_rolls_back_checkpoint_refunds_and_allows_new_attempt(client,monkeypatch,db):
    from app.graphs.practice import PracticeDeps
    from app.db.models import PracticeSession
    calls=[]
    async def notes(*a):return []
    async def review(*a):
        calls.append(a)
        if len(calls)==1:raise RuntimeError('review provider failed')
        return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Reviewed').model_dump(),{}
    async def hint(**kw):return 'Question'
    monkeypatch.setattr('app.routers.practice.default_deps',lambda:PracticeDeps(notes,lambda *a:(True,''),review,hint,lambda p:None))
    headers,uid=await register(client)
    sid=(await client.post('/practice/sessions',headers=headers,json={'problem_id':'two-sum','language':'java'})).json()['session_id']
    body={'action':'submit','code':'public int[] twoSum(int[] a,int t){return new int[]{0,1};}'}
    headers['Idempotency-Key']='failed-graph-action'
    assert (await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=body)).status_code==502
    snapshot=(await client.get('/practice/sessions/'+sid,headers=headers)).json()
    assert snapshot['awaiting']=='learner' and snapshot['attempts']==0
    assert (await client.get('/auth/me',headers=headers)).json()['peppercorns']==settings.signup_bonus
    assert (await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=body)).status_code==502
    assert len(calls)==1
    headers['Idempotency-Key']='new-graph-action'
    retried=await client.post(f'/practice/sessions/{sid}/actions',headers=headers,json=body)
    assert retried.status_code==200 and retried.json()['attempts']==1,retried.text


async def test_self_critique_failure_does_not_return_an_unaudited_draft(monkeypatch):
    from app.services import deep_review as review
    async def evidence(*a,**kw):return {}
    async def draft(**kw):return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Draft')
    class FailedCritique:
        def with_structured_output(self,*a):return self
        async def ainvoke(self,*a):raise RuntimeError('critique unavailable')
    monkeypatch.setattr(review,'gather_evidence',evidence)
    monkeypatch.setattr(review,'analyze_solution',draft)
    monkeypatch.setattr(review,'get_llm',lambda *a:FailedCritique())
    with pytest.raises(RuntimeError,match='critique unavailable'):
        await review.deep_review('two-sum','code','java','gemini')


async def test_admin_credit_retry_is_one_ledger_entry(client,db):
    headers, uid = await register(client)
    user = await db.get(User,uid)
    user.role = 'admin'
    await db.commit()
    headers['Idempotency-Key'] = 'outage-credit'
    url = f'/admin/users/{uid}/peppercorns'
    first = await client.post(url,headers=headers,params={'amount':7,'reason':'outage'})
    again = await client.post(url,headers=headers,params={'amount':7,'reason':'outage'})
    assert first.status_code == 200 and again.json() == first.json()
    assert first.json()['peppercorns'] == settings.signup_bonus + 7
    changed = await client.post(url,headers=headers,params={'amount':8,'reason':'outage'})
    assert changed.status_code == 409
    assert await db.scalar(select(func.count()).select_from(Transaction).where(Transaction.user_id==uid,Transaction.reason=='admin:outage')) == 1
