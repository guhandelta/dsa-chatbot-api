"""Role boundaries apply to direct URLs, replayed requests and existing sessions."""
from datetime import datetime, timedelta, timezone
import json
import pytest
from sqlalchemy import select
from app.core.security import create_access_token
from app.db.models import User, Subscription, InstructorLanguage, KnowledgeDocument, Submission, PracticeSession
from app.services import language_access as access


async def account(db, role='student', languages=()):
    user = User(email=f'{role}-{id(languages)}-{len((await db.scalars(select(User))).all())}@scope.example',
                hashed_password='unused', role=role, peppercorns=50)
    db.add(user); await db.flush()
    for language in languages:
        db.add(Subscription(user_id=user.id, language=language, status='active',
                            expires_at=datetime.now(timezone.utc)+timedelta(days=2)))
    await db.commit()
    return user, {'Authorization': 'Bearer '+create_access_token(user.id)}


async def test_role_access_sources_and_expiry(db):
    student, _ = await account(db, languages=('java','javascript'))
    assert await access.allowed_languages(db, student) == ['java','javascript']
    sub = await db.scalar(select(Subscription).where(Subscription.user_id==student.id, Subscription.language=='java'))
    sub.status='cancelled'; await db.commit()
    assert 'java' in await access.allowed_languages(db, student)
    sub.expires_at=datetime.now(timezone.utc)-timedelta(seconds=1); await db.commit()
    assert await access.allowed_languages(db, student) == ['javascript']
    teacher, _ = await account(db, role='instructor')
    assert not await access.allowed_languages(db, teacher)
    db.add(InstructorLanguage(user_id=teacher.id,language='java',assigned_by=teacher.id))
    upload=KnowledgeDocument(owner_id=teacher.id,filename='Python notes.md',language='python',status='pending')
    db.add(upload); await db.commit()
    assert await access.allowed_languages(db, teacher)==['java','python']
    upload.status='rejected'; await db.commit()
    assert await access.allowed_languages(db, teacher)==['java']
    teacher.role='student'; await db.commit()
    assert not await access.allowed_languages(db, teacher)
    admin,_=await account(db, role='admin')
    assert set(await access.allowed_languages(db,admin))==set(access.available_languages())


@pytest.mark.parametrize('method,url,payload', [
    ('get','/tracks/language/levels?language=java',None),
    ('get','/tracks/language/items?language=java',None),
    ('get','/tracks/language/progress?language=java',None),
    ('get','/tracks/items/java-path-01-values',None),
    ('get','/problems/two-sum?language=java',None),
    ('get','/problems/two-sum/solution-access?language=java',None),
    ('get','/problems/two-sum/solution?language=java',None),
    ('patch','/auth/me/language',{'language':'java'}),
    ('post','/chat/',{'message':'Teach Java','language':'java','track':'language'}),
    ('post','/analyze/',{'problem_id':'two-sum','language':'java','user_code':'code'}),
    ('post','/mentor/ask',{'problem_id':'two-sum','language':'java','reasoning':'Compare values'}),
    ('post','/practice/sessions',{'problem_id':'two-sum','language':'java'}),
    ('post','/mentor/reflect?problem_id=two-sum&language=java&reasoning=notes',None),
])
async def test_student_cannot_bypass_language_scope(client,db,method,url,payload):
    user,h=await account(db,languages=('javascript',))
    kwargs={'headers':h}
    if payload is not None:kwargs['json']=payload
    response=await client.request(method,url,**kwargs)
    assert response.status_code==403,response.text
    assert (await client.get('/auth/me',headers=h)).json()['peppercorns']==50


async def test_reference_subjects_filter_by_role_and_subscription(client,db):
    student,h=await account(db,languages=('java',))
    subjects=(await client.get('/tracks/reference-subjects',headers=h)).json()['subjects']
    assert subjects and all(s['language']=='java' for s in subjects)
    view=(await client.get('/auth/me/access',headers=h)).json()
    assert view['languages']==['java'] and view['preferred_language']=='java' and not view['can_train']
    teacher,t=await account(db,role='instructor')
    assert (await client.get('/tracks/',headers=t)).json()['languages']==[]
    assert (await client.get('/auth/me/access',headers=t)).json()['can_train']
    admin,a=await account(db,role='admin')
    assert 'html' in (await client.get('/tracks/',headers=a)).json()['languages']


async def test_teaching_assignment_requires_admin_and_takes_effect_immediately(client,db):
    admin,a=await account(db,role='admin');teacher,t=await account(db,role='instructor')
    url=f'/admin/users/{teacher.id}/languages'
    assert (await client.put(url,headers=t,json={'languages':['java']})).status_code==403
    r=await client.put(url,headers=a,json={'languages':['java']})
    assert r.status_code==200,r.text
    assert r.json()['assigned_languages']==r.json()['languages']==['java']
    assert (await client.get('/problems/two-sum?language=java',headers=t)).status_code==200
    assert (await client.put(url,headers=a,json={'languages':['bogus']})).status_code==422
    await client.put(url,headers=a,json={'languages':[]})
    assert (await client.get('/problems/two-sum?language=java',headers=t)).status_code==403
    student,s=await account(db)
    assert (await client.put(f'/admin/users/{student.id}/languages',headers=a,json={'languages':['java']})).status_code==409


async def test_first_instructor_upload_confers_language_but_not_student_access(client,db):
    teacher,t=await account(db,role='instructor')
    r=await client.post('/learn/train',headers=t,json={'filename':'Java reading.md','text':'## Types\nPrimitive values and reference values have different semantics.','track':'language','language':'java'})
    assert r.status_code==200,r.text
    assert (await client.get('/auth/me/access',headers=t)).json()['languages']==['java']
    assert (await client.get('/mentor/entitlement?language=java',headers=t)).json()['entitled']
    await client.delete('/learn/documents/'+r.json()['document_id'],headers=t)
    assert (await client.get('/auth/me/access',headers=t)).json()['languages']==[]
    student,s=await account(db,languages=('java',))
    assert (await client.post('/learn/train',headers=s,json={'text':'Some long training notes'})).status_code==403


async def test_only_supplied_submission_languages_establish_teaching_scope(db):
    teacher,_=await account(db,role='instructor')
    db.add(Submission(user_id=teacher.id,problem_id='demo',status='needs_review',raw_input=json.dumps({'hint':'problem','supplied':{'java':'code','python':''}}),markdown='Generated Python and JavaScript too'))
    await db.commit()
    assert await access.allowed_languages(db,teacher)==['java']


async def test_receipt_and_history_do_not_bypass_expired_access(client,db,monkeypatch):
    student,h=await account(db,languages=('java',));h['Idempotency-Key']='scope-retry'
    calls=[]
    async def reply(**kw):calls.append(kw);return 'A Java reference.'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    payload={'message':'Types','language':'java','track':'language'}
    r=await client.post('/chat/',headers=h,json=payload);assert r.status_code==200,r.text
    tid=r.json()['thread_id']
    assert (await client.get(f'/chat/threads/{tid}/messages',headers=h)).status_code==200
    sub=await db.scalar(select(Subscription).where(Subscription.user_id==student.id))
    sub.expires_at=datetime.now(timezone.utc)-timedelta(seconds=1);await db.commit()
    assert (await client.post('/chat/',headers=h,json=payload)).status_code==403
    assert (await client.get(f'/chat/threads/{tid}/messages',headers=h)).status_code==403
    assert (await client.get('/chat/threads',headers=h)).json()==[]
    assert len(calls)==1


async def test_thread_scope_cannot_be_changed_to_import_foreign_history(client,db,monkeypatch):
    user,h=await account(db,languages=('java','javascript'))
    async def reply(**kw):return 'Bounded reference.'
    monkeypatch.setattr('app.routers.chat.run_rag_chat',reply)
    r=await client.post('/chat/',headers=h,json={'message':'Types','language':'java','track':'language'})
    r=await client.post('/chat/',headers=h,json={'message':'Types','language':'javascript','track':'language','thread_id':r.json()['thread_id']})
    assert r.status_code==409


async def test_saved_session_and_actions_recheck_access(client,db):
    user,h=await account(db,languages=('javascript',))
    item=PracticeSession(user_id=user.id,problem_id='two-sum',language='java',provider='gemini')
    db.add(item);await db.commit()
    assert (await client.get('/practice/sessions/'+item.id,headers=h)).status_code==403
    assert (await client.post('/practice/sessions/'+item.id+'/actions',headers=h,json={'action':'submit','code':'ignored'})).status_code==403


@pytest.mark.parametrize('url',['/problems/','/problems/two-sum','/training/registry','/training/registry/history','/training/registry/technologies','/training/status'])
async def test_protected_catalogs_require_authentication(client,url):
    assert (await client.get(url)).status_code==401


async def test_registry_and_training_require_instructor_or_admin(client,db,monkeypatch):
    monkeypatch.setattr('app.services.training_registry.get_training_registry', lambda: {'status': 'ok'})
    monkeypatch.setattr('app.services.training_registry.get_training_history', lambda **kwargs: [])
    monkeypatch.setattr('app.services.training_registry.get_trained_technologies', lambda: [])
    monkeypatch.setattr('app.routers.training.available_languages', lambda: {})
    for role in ('student','instructor','admin'):
        user,h=await account(db,role=role)
        urls = ('/training/registry', '/training/registry/history', '/training/registry/technologies', '/training/status', '/learn/status')
        for url in urls:
            assert (await client.get(url,headers=h)).status_code==(403 if role=='student' else 200)
        user.status = 'suspended'
        await db.commit()
        for url in urls:
            assert (await client.get(url,headers=h)).status_code == 403
