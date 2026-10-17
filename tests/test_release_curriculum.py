"""Release contracts: real curriculum execution and solution authorization."""
import re
import pytest
from sqlalchemy import select
from app.db.models import LearningEvent
from app.models.schemas import AnalysisResult
from app.services.content_catalog import filter_content, load_test_cases
from app.services.content_access import evaluation_completed, solution_document
from app.services.code_runner import available_languages, run_suite

PATH = re.compile(r"^(java|javascript)-path-\d{2}-")
LESSONS = [c for c in filter_content(track="language") if PATH.match(c.id)]


def test_common_curriculum_is_complete_and_ordered():
    for lang in ("javascript", "java"):
        rows = sorted([c for c in LESSONS if c.language == lang], key=lambda c: c.order)
        assert [c.order for c in rows] == list(range(1,13))
        for i, item in enumerate(rows):
            assert item.has_tests and item.starter_code and item.level
            assert item.prerequisites == ([rows[i-1].id] if i else [])
            cases, expected, fns, _ = load_test_cases(item.id)
            assert len(cases) == len(expected) == 6 and fns[lang]
    assert [c.id.split('-path-')[1] for c in sorted(LESSONS,key=lambda c:c.order) if c.language=='java'] == [c.id.split('-path-')[1] for c in sorted(LESSONS,key=lambda c:c.order) if c.language=='javascript']


@pytest.mark.parametrize("item", LESSONS, ids=lambda c: c.id)
def test_reference_exercises_execute(item):
    if not available_languages().get(item.language):
        pytest.skip(f"{item.language} runtime unavailable")
    cases, expected, fns, io_mode = load_test_cases(item.id)
    code = re.search(r"```\w+\n(.*?)```", solution_document(item.id,item.language), re.S).group(1)
    report = run_suite({item.language:code}, fns, cases, expected, io_mode)
    result = report['results'][0]
    assert result['tier'] == 1 and result['status'] == 'passed', result
    assert result['passed_cases'] == 6


async def register(client, email):
    r = await client.post('/auth/register', json={'email':email,'password':'password123'})
    return {'Authorization': 'Bearer ' + r.json()['access_token']}, r.json()['user']['id']


async def test_statements_never_expose_references_or_hidden_cases(client):
    headers, _ = await register(client,'statement@example.com')
    for cid in ['two-sum','javascript-path-01-values','java-path-07-maps']:
        for url in [f'/problems/{cid}',f'/tracks/items/{cid}']:
            r=await client.get(url,headers=headers)
            assert r.status_code==200
            body=r.json()['markdown']
            assert '## Solutions' not in body and '## Approach' not in body
            assert 'test_cases:' not in body and 'expected' not in body
        assert (await client.get(f'/problems/{cid}/solution?language=java',headers=headers)).status_code==403
    assert (await client.get('/problems/two-sum/solution?language=java')).status_code==401


@pytest.mark.parametrize('status,tier,total,unlocks', [('passed',1,6,True),('failed',1,6,True),('error',1,6,False),('unverified',2,0,False),('passed',2,0,False)])
async def test_reveal_requires_own_completed_evaluation(client,monkeypatch,session_factory,status,tier,total,unlocks):
    headers, uid = await register(client,'learner@example.com')
    other, _ = await register(client,'other@example.com')
    async def review(**kwargs):
        return AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Feedback'), {'curated':{'results':[{'language':'javascript','tier':tier,'status':status,'total_cases':total,'passed_cases':6 if status=='passed' else 0}]}}
    monkeypatch.setattr('app.routers.analyze.deep_review', review)
    r=await client.post('/analyze/',headers=headers,json={'problem_id':'javascript-path-01-values','user_code':'function totalCost(price, quantity) { return 0; }','language':'javascript','provider':'openai'})
    assert r.status_code==200,r.text
    assert r.json()['solution_available'] is unlocks
    url='/problems/javascript-path-01-values/solution?language=javascript'
    result=await client.get(url,headers=headers)
    assert result.status_code==(200 if unlocks else 403)
    if unlocks:
        assert 'return price * quantity' in result.json()['markdown']
    assert (await client.get(url,headers=other)).status_code==403
    assert (await client.get('/problems/javascript-path-01-values/solution?language=java',headers=headers)).status_code==403
    async with session_factory() as session:
        solved=await session.scalar(select(LearningEvent.id).where(LearningEvent.user_id==uid,LearningEvent.kind=='solved'))
        assert bool(solved)==(status=='passed' and tier==1 and total>0)


async def test_provider_failure_does_not_unlock(client,monkeypatch):
    headers,_=await register(client,'failure@example.com')
    async def broken(**kwargs): raise RuntimeError('provider unavailable')
    monkeypatch.setattr('app.routers.analyze.deep_review',broken)
    r=await client.post('/analyze/',headers=headers,json={'problem_id':'two-sum','user_code':'function twoSum(nums, target) { return []; }','language':'javascript','provider':'openai'})
    assert r.status_code==502
    assert (await client.get('/problems/two-sum/solution?language=javascript',headers=headers)).status_code==403


def test_empty_evidence_is_not_completed():
    assert not evaluation_completed({},'java')


def test_packaged_corpus_and_local_retrieval_are_answer_safe():
    from app.services.curriculum import records, retrieval_documents
    from app.services.curriculum_search import search
    assert len(records()) == 4280
    docs=list(retrieval_documents())
    assert docs and all(d.metadata['contains_answer'] is False for d in docs)
    assert not any(d.metadata['kind'] in ('gotcha','exercise') for d in docs)
    for lang in ('java','javascript'):
        results=search('map key value insertion order', 'language', lang)
        assert results and all(d.metadata['language']==lang for d in results)
    results=search('help with the exercise', 'language', 'java', 'java-path-01-values')
    assert results and all(d.metadata['problem_id']=='java-path-01-values' for d in results)
    assert not search('map', 'language', 'java', 'does-not-exist')


async def test_progress_is_owned_and_language_scoped(client,session_factory):
    headers,uid=await register(client,'progress@example.com')
    other,_=await register(client,'progress-other@example.com')
    async with session_factory() as session:
        session.add(LearningEvent(user_id=uid,problem_id='java-path-01-values',language='java',kind='solved'))
        session.add(LearningEvent(user_id=uid,problem_id='java-path-02-conditions',language='java',kind='attempt'))
        await session.commit()
    p=(await client.get('/tracks/language/progress?language=java',headers=headers)).json()
    assert p=={'completed_ids':['java-path-01-values'],'total':12,'next_id':'java-path-02-conditions'}
    assert (await client.get('/tracks/language/progress?language=javascript',headers=headers)).json()['completed_ids']==[]
    assert (await client.get('/tracks/language/progress?language=java',headers=other)).json()['completed_ids']==[]


async def test_unknown_or_wrong_language_exercise_is_not_evaluated(client,monkeypatch):
    headers,_=await register(client,'invalid-exercise@example.com')
    calls=[]
    async def review(**kwargs): calls.append(kwargs); raise AssertionError('should not evaluate')
    monkeypatch.setattr('app.routers.analyze.deep_review',review)
    request={'problem_id':'javascript-path-01-values','user_code':'public int totalCost(int a, int b) { return 0; }','language':'java'}
    assert (await client.post('/analyze/',headers=headers,json=request)).status_code==400
    request['problem_id']='does-not-exist'
    assert (await client.post('/analyze/',headers=headers,json=request)).status_code==404
    assert calls==[]
