import pytest

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.models import StudentPathRecord, Subscription, User


async def register(client, email):
    response = await client.post('/auth/register', json={'email': email, 'password': 'password123'})
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_records_are_scoped_and_not_mastery(client, db, subscribe_user):
    first = await register(client, 'records-first@example.com')
    second = await register(client, 'records-second@example.com')
    await subscribe_user(first['user']['id'], 'javascript')
    await subscribe_user(second['user']['id'], 'javascript')
    headers = {'Authorization': f"Bearer {first['access_token']}"}
    other = {'Authorization': f"Bearer {second['access_token']}"}
    entry = {'section': 'design-patterns', 'language': 'javascript', 'kind': 'assumption',
             'concept_id': 'design-patterns:strategy:javascript',
             'body': '  A callback is always clearer than a conditional.  '}
    result = await client.post('/learning-records/', headers=headers, json=entry)
    assert result.status_code == 201, result.text
    assert result.json()['body'] == 'A callback is always clearer than a conditional.'
    assert result.json()['curriculum_version'] == 1
    goal = await client.post('/learning-records/', headers=headers, json={
        'section': 'dsa', 'language': 'javascript', 'kind': 'goal',
        'body': 'Learn binary search invariants',
    })
    assert goal.status_code == 201
    assert goal.json()['concept_id'] is None
    own = await client.get('/learning-records/', headers=headers,
                           params={'section': 'design-patterns', 'language': 'javascript'})
    assert [item['id'] for item in own.json()['items']] == [result.json()['id']]
    stranger = await client.get('/learning-records/', headers=other,
                                params={'section': 'design-patterns', 'language': 'javascript'})
    assert stranger.json()['items'] == []
    dsa = await client.get('/learning-records/', headers=headers,
                           params={'section': 'dsa', 'language': 'javascript'})
    assert [item['id'] for item in dsa.json()['items']] == [goal.json()['id']]
    assert (await db.get(StudentPathRecord, result.json()['id'])).user_id == first['user']['id']
    path = await client.get('/study/path', headers=headers, params={'language': 'javascript'})
    assert path.status_code == 200
    assert path.json()['completed'] == 0


@pytest.mark.asyncio
async def test_record_rejects_wrong_scope_and_unsupported_claims(client, subscribe_user):
    account = await register(client, 'records-validation@example.com')
    await subscribe_user(account['user']['id'], 'javascript')
    headers = {'Authorization': f"Bearer {account['access_token']}"}
    base = {'section': 'language', 'language': 'javascript', 'kind': 'goal', 'body': 'Understand callbacks'}
    for changes, status in [
        ({'language': 'python'}, 403),
        ({'section': 'unknown'}, 422),
        ({'body': '   '}, 422),
        ({'kind': 'assumption'}, 422),
        ({'concept_id': 'absent'}, 422),
        ({'concept_id': 'design-patterns:strategy:javascript'}, 422),
        ({'concept_id': 'language:python:functions'}, 422),
    ]:
        response = await client.post('/learning-records/', headers=headers, json={**base, **changes})
        assert response.status_code == status, response.text
    assert (await client.get('/learning-records/', headers=headers,
                             params={'section': 'language', 'language': 'python'})).json()['items'] == []
    assert (await client.get('/learning-records/', headers=headers,
                             params={'section': 'language', 'language': 'javascript', 'limit': 101})).status_code == 422
    assert (await client.get('/learning-records/', params={'section': 'language', 'language': 'javascript'})).status_code == 401


@pytest.mark.asyncio
async def test_concept_language_must_match_even_when_both_languages_are_entitled(client, subscribe_user):
    account = await register(client, 'records-multilang@example.com')
    await subscribe_user(account['user']['id'], 'javascript', 'python')
    headers = {'Authorization': f"Bearer {account['access_token']}"}
    for section, concept_id in [
        ('language', 'language:javascript:functions'),
        ('design-patterns', 'design-patterns:strategy:javascript'),
    ]:
        result = await client.post('/learning-records/', headers=headers, json={
            'section': section, 'language': 'python', 'kind': 'decision',
            'concept_id': concept_id, 'body': 'Use a callback',
        })
        assert result.status_code == 422


@pytest.mark.asyncio
async def test_export_and_erase_include_only_owner_records(client, db, subscribe_user):
    first = await register(client, 'records-export-first@example.com')
    second = await register(client, 'records-export-second@example.com')
    await subscribe_user(first['user']['id'], 'javascript')
    await subscribe_user(second['user']['id'], 'javascript')
    headers = {'Authorization': f"Bearer {first['access_token']}"}
    other = {'Authorization': f"Bearer {second['access_token']}"}
    entry = {'section': 'dsa', 'language': 'javascript', 'kind': 'goal', 'body': 'Review invariants'}
    own = (await client.post('/learning-records/', headers=headers, json=entry)).json()
    theirs = (await client.post('/learning-records/', headers=other, json=entry)).json()
    exported = (await client.get('/mentor/profile/export', headers=headers)).json()
    assert [record['id'] for record in exported['student_path_records']] == [own['id']]
    assert (await client.delete('/mentor/profile', headers=headers)).status_code == 200
    assert await db.get(StudentPathRecord, own['id']) is None
    assert await db.get(StudentPathRecord, theirs['id']) is not None


@pytest.mark.asyncio
async def test_expired_student_can_read_history_but_not_add_records(client, db, subscribe_user):
    account = await register(client, 'records-expired@example.com')
    user_id = account['user']['id']
    await subscribe_user(user_id, 'javascript')
    headers = {'Authorization': f"Bearer {account['access_token']}"}
    entry = {'section': 'dsa', 'language': 'javascript', 'kind': 'goal', 'body': 'Review invariants'}
    saved = await client.post('/learning-records/', headers=headers, json=entry)
    assert saved.status_code == 201
    subscription = await db.scalar(select(Subscription).where(Subscription.user_id == user_id))
    subscription.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    await db.commit()
    history = await client.get('/learning-records/', headers=headers,
                               params={'section': 'dsa', 'language': 'javascript'})
    assert [item['id'] for item in history.json()['items']] == [saved.json()['id']]
    assert (await client.post('/learning-records/', headers=headers, json=entry)).status_code == 403
    user = await db.get(User, user_id)
    user.status = 'suspended'
    await db.commit()
    assert (await client.get('/learning-records/', headers=headers,
                             params={'section': 'dsa', 'language': 'javascript'})).status_code == 403
