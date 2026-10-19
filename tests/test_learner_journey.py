"""HTTP learner journey with real execution, SQL checkpoints and receipts.

Only model generation/retrieval infrastructure is faked. Published references
and submitted code actually run in the configured local development executor.
"""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import select,func

from app.core.config import settings
from app.db.models import LearningEvent, Subscription
from app.models.schemas import AnalysisResult


@pytest.mark.parametrize('language,wrong,right',[
    ('javascript','function totalCost(price,quantity){return price+quantity;}',
                  'function totalCost(price,quantity){return price*quantity;}'),
    ('java','public int totalCost(int price,int quantity){return price+quantity;}',
            'public int totalCost(int price,int quantity){return price*quantity;}'),
])
async def test_fail_hint_resume_pass_reveal_reflect_with_real_execution(client,db,monkeypatch,language,wrong,right):
    feedback = AnalysisResult(mistakes=[],enhancements=[],watchouts=[],interview_tips=[],overall_feedback='Use the execution evidence to check your reasoning.')
    async def draft(**kwargs):return feedback
    class Model:
        def with_structured_output(self,*args):return self
        async def ainvoke(self,prompt):return feedback
    class HintModel:
        async def ainvoke(self,messages):return SimpleNamespace(content='What does each quantity represent in your calculation?')
    monkeypatch.setattr('app.services.deep_review.analyze_solution',draft)
    monkeypatch.setattr('app.services.deep_review.get_llm',lambda _:Model())
    monkeypatch.setattr('app.services.mentor.get_llm',lambda _:HintModel())
    monkeypatch.setattr('app.services.knowledge_base.get_vectorstore',lambda:SimpleNamespace(similarity_search=lambda *a,**kw:[]))
    registered = (await client.post('/auth/register',json={'email':'journey@example.com','password':'password123'})).json()
    uid=registered['user']['id']
    headers={'Authorization':'Bearer '+registered['access_token']}
    db.add(Subscription(user_id=uid,language=language,expires_at=datetime.now(timezone.utc)+timedelta(days=42)))
    await db.commit()
    pid=f'{language}-path-01-values'
    assert (await client.get(f'/problems/{pid}/solution',headers=headers,params={'language':language})).status_code==403
    assert (await client.post('/mentor/reflect',headers=headers,params={'problem_id':pid,'language':language,'reasoning':'Not solved yet'})).status_code==403
    started=await client.post('/practice/sessions',headers={**headers,'Idempotency-Key':'start'},json={'problem_id':pid,'language':language})
    assert started.status_code==200,started.text
    sid=started.json()['session_id']
    path=f'/practice/sessions/{sid}/actions'
    failed=await client.post(path,headers={**headers,'Idempotency-Key':'wrong'},json={'action':'submit','code':wrong})
    assert failed.status_code==200,failed.text
    assert failed.json()['outcome']=='failed' and failed.json()['awaiting']=='learner'
    result=failed.json()['evidence']['curated']['results'][0]
    assert result['total_cases']>=6 and result['passed_cases']<result['total_cases']
    assert failed.json()['solution_available'] is True
    assert 'markdown' not in failed.json()  # available only via explicit reveal endpoint
    assert (await client.post(path,headers=headers,json={'action':'reflect','reasoning':'Claimed success'})).status_code==409
    hinted=await client.post(path,headers={**headers,'Idempotency-Key':'hint'},json={'action':'hint','reasoning':'I added price and quantity, but the totals differ.'})
    assert hinted.status_code==200 and hinted.json()['hint_tier']==1,hinted.text
    assert hinted.json()['peppercorns_charged']==0 and hinted.json()['next_hint_cost']==0
    assert hinted.json()['peppercorns_remaining']==settings.signup_bonus-settings.analyze_cost
    resumed=await client.get(f'/practice/sessions/{sid}',headers=headers)
    assert resumed.json()['attempts']==1 and resumed.json()['awaiting']=='learner'
    submission={'action':'submit','code':right}
    passed=await client.post(path,headers={**headers,'Idempotency-Key':'right'},json=submission)
    assert passed.status_code==200,passed.text
    assert passed.json()['outcome']=='passed' and passed.json()['awaiting']=='reflection'
    assert [r['reason'] for r in passed.json()['rewards']]==['earn:independent_solve']
    assert passed.json()['peppercorns_remaining']==settings.signup_bonus-2*settings.analyze_cost+settings.reward_independent_solve
    retry=await client.post(path,headers={**headers,'Idempotency-Key':'right'},json=submission)
    assert retry.json()==passed.json()
    assert (await client.get(f'/problems/{pid}/solution',headers=headers,params={'language':language})).status_code==200
    reflection=await client.post(path,headers={**headers,'Idempotency-Key':'reflection'},json={'action':'reflect','reasoning':'Equal amounts repeat, so I multiply price and quantity.'})
    assert reflection.status_code==200 and reflection.json()['awaiting'] is None,reflection.text
    profile=(await client.get('/mentor/profile',headers=headers)).json()
    assert profile['solved']==1
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id==uid,LearningEvent.kind=='reflection'))==1
    remaining=(await client.get('/auth/me',headers=headers)).json()['peppercorns']
    # The tier-1 hint was free and the first solve used no paid tier, so it
    # earned the independent-solve reward back.
    assert remaining==settings.signup_bonus-2*settings.analyze_cost+settings.reward_independent_solve
