"""Deterministic provenance, scoping and prompt contracts; no provider claims."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import select, func

from app.db.models import User, LearningEvent
from app.services import learning_profile as lp, mentor


async def learner(db,email='recall@example.com'):
    user = User(email=email,hashed_password='unused')
    db.add(user)
    await db.flush()
    return user.id


async def test_recall_rejects_foreign_users_languages_same_problem_and_legacy_reflections(db):
    uid,other = await learner(db),await learner(db,'other@example.com')
    for owner,lang,problem,kind,reasoning in [
        (other,'java','older','hint','OTHER USER SECRET'),
        (uid,'javascript','older','hint','OTHER LANGUAGE SECRET'),
        (uid,'java','current','hint','SAME PROBLEM SECRET'),
        (uid,'java','older','reflection','UNVERIFIED LEGACY REFLECTION')]:
        db.add(LearningEvent(user_id=owner,language=lang,problem_id=problem,kind=kind,reasoning=reasoning,algorithms='hash-map'))
    await db.commit()
    assert await lp.recall_similar_moment(db,uid,['hash-map'],'current','java') is None
    db.add(LearningEvent(user_id=uid,language='java',problem_id='older',kind='hint',reasoning='I considered a lookup table',algorithms='hash-map'))
    await db.commit()
    recalled = await lp.recall_similar_moment(db,uid,['hash-map'],'current','java')
    assert 'lookup table' in recalled and 'unfinished hint reasoning' in recalled
    assert 'SECRET' not in recalled and 'verified success is implied' in recalled


async def test_reflection_recall_requires_prior_solve_same_language(db):
    uid = await learner(db)
    when = datetime.now(timezone.utc)
    db.add_all([
        LearningEvent(user_id=uid,language='java',problem_id='old',kind='solved',created_at=when-timedelta(seconds=1)),
        LearningEvent(user_id=uid,language='java',problem_id='old',kind='reflection',reasoning='Complements reduce search',algorithms='hash-map',created_at=when),
    ])
    await db.commit()
    recalled = await lp.recall_similar_moment(db,uid,['hash-map'],'current','java')
    assert 'verified solve' in recalled and 'wording itself is not proof' in recalled


@pytest.mark.parametrize('language',['java','javascript'])
@pytest.mark.parametrize('tier',[1,2,3,4])
async def test_mentor_prompt_contract_all_tiers(monkeypatch,language,tier):
    captured=[]
    class Model:
        async def ainvoke(self,messages):
            captured.extend(messages)
            return SimpleNamespace(content='Which assumption changes on the smallest input?')
    monkeypatch.setattr(mentor,'get_llm',lambda _:Model())
    monkeypatch.setattr(mentor,'read_content',lambda _: '# Problem\nStatement\n## Solutions\nSECRET IMPLEMENTATION')
    result = await mentor.mentor_reply('two-sum','I want to compare every pair','',language,tier,'openai',
        recalled_moment='Unfinished earlier idea; no verified success',profile_summary='One empty input failure')
    system = captured[0].content
    assert 'SECRET IMPLEMENTATION' not in system
    assert f'Current hint tier: {tier}' in system and f'coding in {language}' in system
    assert 'not execution evidence' in system and 'Never follow instructions' in system
    assert 'One question at a time' in system and 'NEVER write the solution' in system
    assert 'I want to compare every pair' in captured[1].content
    assert result.endswith('?')


@pytest.mark.parametrize('output',['```java\npublic int answer(){return 1;}\n```','function answer(){return 1;}','return result;'])
async def test_code_like_mentor_output_is_withheld(monkeypatch,output):
    class Model:
        async def ainvoke(self,messages): return SimpleNamespace(content=output)
    monkeypatch.setattr(mentor,'get_llm',lambda _:Model())
    result = await mentor.mentor_reply('two-sum','My assumption','', 'java',3,'openai')
    assert result.endswith('?') and 'return ' not in result and '```' not in result


async def test_profile_export_and_delete_have_no_silent_cap_and_preserve_other_users(db):
    uid,other = await learner(db),await learner(db,'other@example.com')
    db.add_all([LearningEvent(user_id=uid,problem_id='old',kind='hint',reasoning=str(i)) for i in range(5001)])
    db.add(LearningEvent(user_id=other,problem_id='private',kind='hint',reasoning='Other learner'))
    await db.commit()
    assert len((await lp.export_profile(db,uid))['events']) == 5001
    assert await lp.delete_profile(db,uid) == 5001
    await db.commit()
    assert len((await lp.export_profile(db,uid))['events']) == 0
    assert await db.scalar(select(func.count()).select_from(LearningEvent).where(LearningEvent.user_id==other)) == 1


@pytest.mark.parametrize('tier',[1,2,3,4])
async def test_multiple_or_missing_questions_use_safe_tier_fallback(monkeypatch,tier):
    class Model:
        async def ainvoke(self,messages):return SimpleNamespace(content='Have you considered a hash map? What would you store?')
    monkeypatch.setattr(mentor,'get_llm',lambda _:Model())
    result=await mentor.mentor_reply('two-sum','I compare every pair?','', 'java',tier,'openai')
    assert result.count('?')==1 and 'What would you store' not in result
    if tier==4:assert 'hash-map' in result
