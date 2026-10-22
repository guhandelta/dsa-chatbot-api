"""Debugging bank coverage, no-repeat reservations, and subscription isolation."""
import asyncio
from collections import Counter
from datetime import datetime, timedelta, timezone
import json

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import DebugChallengeAttempt, Subscription
from app.services import debug_challenges as dc, reference_library
from tests.test_language_access import account


def test_bank_covers_every_catalog_subject_at_all_five_levels():
    from tools.audit_debug_challenges import audit
    assert not audit()['errors']
    items = dc.bank()
    counts = Counter((i['subject'], i['difficulty']) for i in items.values())
    expected = {s['id']: s['language'] for s in reference_library.subjects()}
    assert {i['subject'] for i in items.values()} == set(expected)
    assert len(items) >= 1500
    for subject, language in expected.items():
        for difficulty in dc.DIFFICULTIES:
            assert counts[subject, difficulty] >= 2, (subject, difficulty)
        assert all(i['language'] == language for i in items.values() if i['subject'] == subject)


def test_bank_is_deduplicated_and_answers_never_reach_public_views():
    seen = set()
    for item in dc.bank().values():
        assert item['code'].strip() and item['failure'].strip() and item['goal'].strip()
        assert item['solution'].strip()
        fingerprint = dc._fingerprint(item['language'], item['subject'], item['code'])
        assert fingerprint == item['id'] and fingerprint not in seen
        seen.add(fingerprint)
        view = dc.public(item)
        assert 'solution' not in view and 'private_solution' not in view
        assert not view['automatically_graded'] and view['assessment'] == 'self-review'
    assert dc._fingerprint('java', 'java', 'a + b') == dc._fingerprint('java', 'java', 'a+b')


async def test_draw_never_repeats_and_exhaustion_never_resets_history(client, db):
    user, headers = await account(db, languages=('python',))
    body = {'language': 'python', 'subject': 'python-fastapi', 'difficulty': 'easy', 'focus_id': 'subject:python-fastapi'}
    seen = []
    for _ in range(2):
        response = await client.post('/study/debug/challenges/next', headers=headers, json=body)
        assert response.status_code == 200, response.text
        item = response.json()
        assert item['id'] not in seen and 'solution' not in item
        seen.append(item['id'])
    response = await client.post('/study/debug/challenges/next', headers=headers, json=body)
    assert response.status_code == 409
    catalog = (await client.get('/study/debug/challenges?language=python&focus_id=subject:python-fastapi', headers=headers)).json()
    level = next(s for s in catalog['subjects'] if s['id'] == 'python-fastapi')['levels'][0]
    assert level['remaining'] == 0 and level['current']['id'] == seen[-1]
    rows = (await db.scalars(select(DebugChallengeAttempt).where(DebugChallengeAttempt.user_id == user.id))).all()
    assert [r.status for r in sorted(rows, key=lambda r:r.created_at)] == ['skipped', 'assigned']
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == 50


async def test_reload_resumes_current_and_review_does_not_fake_mastery(client, db):
    user, headers = await account(db, languages=('java',))
    body = {'language': 'java', 'subject': 'spring-data', 'difficulty': 'extreme', 'focus_id': 'subject:spring-data'}
    item = (await client.post('/study/debug/challenges/next', headers=headers, json=body)).json()
    for _ in range(2):
        catalog = (await client.get('/study/debug/challenges?language=java&focus_id=subject:spring-data', headers=headers)).json()
        level = next(s for s in catalog['subjects'] if s['id'] == 'spring-data')['levels'][-1]
        assert level['remaining'] == 1 and level['current']['attempt_id'] == item['attempt_id']
    url = f"/study/debug/challenges/{item['attempt_id']}/review"
    response = await client.post(url, headers=headers, json={'diagnosis': 'The traversal shifts after mutation; add an interleaving regression test.'})
    assert response.status_code == 200 and response.json()['automatically_graded'] is False
    row = await db.get(DebugChallengeAttempt, item['attempt_id'])
    await db.refresh(row)
    assert row.status == 'reviewed' and row.reviewed_at
    catalog = (await client.get('/study/debug/challenges?language=java&focus_id=subject:spring-data', headers=headers)).json()
    level = next(s for s in catalog['subjects'] if s['id'] == 'spring-data')['levels'][-1]
    assert level['current'] is None and level['reviewed'] == 1 and level['remaining'] == 1
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == 50
    assert (await client.post(url, headers=headers, json={'diagnosis':' '*20})).status_code == 422


@pytest.mark.parametrize('language', ('python','javascript','java','typescript','c','cpp','rust','go','csharp','ruby','html','css'))
async def test_subjects_and_direct_api_calls_follow_subscription(client, db, language):
    user, headers = await account(db, languages=(language,))
    catalog = await client.get('/study/debug/challenges', headers=headers, params={'language': language})
    assert catalog.status_code == 200
    ownership = {s['id']:s['language'] for s in reference_library.subjects()}
    assert catalog.json()['subjects']
    assert all(ownership[s['id']] == language for s in catalog.json()['subjects'])
    foreign = 'java' if language != 'java' else 'python'
    assert (await client.get('/study/debug/challenges', headers=headers, params={'language':foreign})).status_code == 403
    body = {'language':foreign, 'subject':foreign, 'difficulty':'easy'}
    assert (await client.post('/study/debug/challenges/next', headers=headers, json=body)).status_code == 403
    body['language'] = language
    assert (await client.post('/study/debug/challenges/next', headers=headers, json=body)).status_code == 422


async def test_attempt_ownership_and_expiry_apply_to_reviews_and_coaching_focus(client, db):
    owner, h = await account(db, languages=('python',))
    other, o = await account(db, languages=('python',))
    item = (await client.post('/study/debug/challenges/next', headers=h, json={'language':'python','subject':'python','difficulty':'easy'})).json()
    review = f"/study/debug/challenges/{item['attempt_id']}/review"
    assert (await client.post(review, headers=o, json={'diagnosis':'A diagnosis with a regression test.'})).status_code == 404
    with pytest.raises(HTTPException) as e:
        await dc.focus(db, other.id, 'python', item['attempt_id'])
    assert e.value.status_code == 404
    with pytest.raises(HTTPException) as e:
        await dc.focus(db, owner.id, 'java', item['attempt_id'])
    assert e.value.status_code == 403
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == owner.id))
    sub.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await db.commit()
    assert (await client.post(review, headers=h, json={'diagnosis':'A diagnosis with a regression test.'})).status_code == 403
    response = await client.post('/study/message', headers=h, json={
        'language':'python','mode':'debug','focus_id':'debug:'+item['attempt_id'],
        'code':item['code'],'error':item['failure'],'message':'What invariant breaks?'})
    assert response.status_code == 403


async def test_database_rejects_duplicate_assignments_across_requests(db):
    user, _ = await account(db, languages=('go',))
    item = dc.pool('go', 'go', 'easy')[0]
    for n in range(2):
        row = DebugChallengeAttempt(user_id=user.id, challenge_id=item['id'], language='go', subject='go', difficulty='easy')
        if n == 0:
            db.add(row); await db.commit()
        else:
            with pytest.raises(IntegrityError):
                async with db.begin_nested():
                    db.add(row); await db.flush()


async def test_challenge_focus_overrides_path_without_importing_answers(db):
    from app.services import study_room
    user, _ = await account(db, languages=('java',))
    item = await dc.next_challenge(db, user, 'java', 'spring-security', 'extreme')
    focus = await study_room.resolve_focus(db, user.id, 'java', 'debug:' + item['attempt_id'])
    assert 'spring-security' in focus['title'] and focus['id'].startswith('debug:')
    assert 'solution' not in json.dumps(focus)
    prompt = study_room.debug_prompt('java', focus, 1)
    assert focus['goal'] in prompt
    assert dc.bank()[item['id']]['solution'] not in prompt


async def test_concurrent_requests_never_deliver_the_same_problem(tmp_path):
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.db.database import Base
    from app.db.models import User
    engine = create_async_engine('sqlite+aiosqlite:///' + str(tmp_path/'concurrent.db'))
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as session:
        user, _ = await account(session, languages=('java',))
        uid = user.id
    async def reserve():
        async with sessions() as session:
            user = await session.get(User, uid)
            return await dc.next_challenge(session, user, 'java', 'java', 'easy')
    try:
        results = await asyncio.gather(*(reserve() for _ in range(4)))
        assert len({r['id'] for r in results}) == len(results)
        async with sessions() as session:
            rows = (await session.scalars(select(DebugChallengeAttempt).where(DebugChallengeAttempt.user_id==uid))).all()
            assert len(rows) == 4
    finally:
        await engine.dispose()


def test_every_core_path_topic_has_relevant_investigations():
    from app.services import learning_path as lp
    items = dc.bank().values()
    for language in lp.LANGUAGE_LABELS:
        for node in lp.nodes(language):
            scoped = [i for i in items if i['language'] == language and dc.in_scope(i, {'kind':'node','id':node['id']})]
            assert scoped, node['id']
            assert all(i['subject'] == language and node['id'] in i['node_ids'] for i in scoped)
    trace = [i for i in items if i['task_kind'] == 'trace']
    assert trace and all('Do not assume' in i['goal'] for i in trace)


@pytest.mark.parametrize('language', dc.quiz_languages())
async def test_current_topic_filters_catalog_and_draws(client, db, language):
    user, headers = await account(db, languages=(language,))
    node = language + ':stage-01'
    catalog = (await client.get('/study/debug/challenges', headers=headers, params={'language':language,'focus_id':node})).json()
    assert catalog['scope']['id'] == node
    default_catalog = (await client.get('/study/debug/challenges', headers=headers, params={'language':language})).json()
    assert default_catalog['scope']['id'] == node
    assert catalog['scope']['title'] == 'Values and arithmetic'
    assert [s['id'] for s in catalog['subjects']] == [language]
    levels = catalog['subjects'][0]['levels']
    level = next(l for l in levels if l['total'] > 0)
    response = await client.post('/study/debug/challenges/next', headers=headers, json={
        'language':language,'subject':language,'difficulty':level['difficulty'],'focus_id':node})
    assert response.status_code == 200, response.text
    chosen = dc.bank()[response.json()['id']]
    assert node in chosen['node_ids']
    assert 'solution' not in response.json()


async def test_scoped_debugger_never_substitutes_other_topics_or_frameworks(client, db):
    user, headers = await account(db, languages=('python',))
    node = 'python:module-context-managers'
    response = await client.post('/study/debug/challenges/next', headers=headers, json={
        'language':'python','subject':'python','difficulty':'extreme','focus_id':node})
    assert response.status_code == 409
    assert 'unrelated' in response.json()['detail']
    response = await client.post('/study/debug/challenges/next', headers=headers, json={
        'language':'python','subject':'python-fastapi','difficulty':'easy','focus_id':'python:stage-01'})
    assert response.status_code == 409
    response = await client.get('/study/debug/challenges', headers=headers, params={'language':'python','focus_id':'java:stage-01'})
    assert response.status_code in (403,404)


async def test_topic_switch_preserves_each_topics_current_problem(client, db):
    user, headers = await account(db, languages=('python',))
    active = {}
    for node in ('python:stage-01','python:stage-03'):
        catalog = (await client.get('/study/debug/challenges', headers=headers, params={'language':'python','focus_id':node})).json()
        difficulty = next(l['difficulty'] for l in catalog['subjects'][0]['levels'] if l['total'])
        response = await client.post('/study/debug/challenges/next', headers=headers, json={
            'language':'python','subject':'python','difficulty':difficulty,'focus_id':node})
        assert response.status_code == 200
        active[node] = (difficulty, response.json()['attempt_id'])
    for node,(difficulty,attempt) in active.items():
        catalog = (await client.get('/study/debug/challenges', headers=headers, params={'language':'python','focus_id':node})).json()
        level = next(l for l in catalog['subjects'][0]['levels'] if l['difficulty'] == difficulty)
        assert level['current']['attempt_id'] == attempt


async def test_framework_collection_context_is_kept_and_authorized(client, db):
    user, headers = await account(db, languages=('python',))
    response = await client.get('/study/debug/challenges', headers=headers, params={'language':'python','focus_id':'subject:python-fastapi'})
    assert response.status_code == 200
    assert [s['id'] for s in response.json()['subjects']] == ['python-fastapi']
    response = await client.get('/study/debug/challenges', headers=headers, params={'language':'python','focus_id':'subject:spring-data'})
    assert response.status_code == 403
    from app.services import study_room
    focus = await study_room.resolve_focus(db, user.id, 'python', 'subject:python-fastapi')
    assert focus['subject'] == 'python-fastapi'
