from app.db.models import DebugChallengeAttempt, LearningEvent, StudentPathRecord, User
from app.services import debug_challenges as dc
from tests.test_study_room import register


async def test_overview_counts_unique_evidence_and_separates_self_review(client, db):
    headers, uid = await register(client, db)
    _, other = await register(client, db, 'another-progress@example.com')
    for owner, lang, problem, kind in [
        (uid, 'python', 'two-sum', 'solved'), (uid, 'python', 'two-sum', 'solved'),
        (uid, 'python', 'missing-number', 'attempt'),
        (uid, 'javascript', 'missing-number', 'solved'),
        (other, 'python', 'missing-number', 'solved'),
        (uid, 'python', 'python-path-01-values', 'solved'),
    ]:
        db.add(LearningEvent(user_id=owner, language=lang, problem_id=problem, kind=kind))
    cases = [i for i in dc.bank().values() if i['language'] == 'python']
    for case, status in zip(cases, ['reviewed', 'assigned', 'skipped']):
        db.add(DebugChallengeAttempt(user_id=uid, challenge_id=case['id'], language='python',
            subject=case['subject'], difficulty=case['difficulty'], status=status))
    db.add(DebugChallengeAttempt(user_id=uid, challenge_id='retired-case', language='python',
        subject='python', difficulty='easy', status='reviewed'))
    await db.commit()
    result = await client.get('/study/progress-overview', headers=headers, params={'language': 'python'})
    assert result.status_code == 200
    sections = {s['id']: s for s in result.json()['sections']}
    assert sections['dsa']['completed'] == 1
    assert sections['dsa']['in_progress'] == 1
    assert sections['debug']['completed'] == 1
    assert sections['debug']['in_progress'] == 2
    assert sections['debug']['total'] == len(cases)
    assert sections['design-patterns']['completed'] is None
    assert sections['design-patterns']['status'] == 'coming-soon'
    assert sections['design-patterns']['lessons_available'] > 0
    assert (await client.get('/study/progress-overview', headers=headers,
                             params={'language': 'rust'})).status_code == 403


def test_runtime_debug_bank_does_not_read_quizzes_or_reference_cases(monkeypatch):
    monkeypatch.setattr('app.services.quiz._authored', lambda *a: (_ for _ in ()).throw(AssertionError('quiz read')))
    monkeypatch.setattr('app.services.reference_library.records', lambda: (_ for _ in ()).throw(AssertionError('reference read')))
    dc._bank.cache_clear()
    assert len(dc.bank()) >= 1500


async def test_profile_overview_keeps_sections_and_student_records_separate(client, db):
    headers, uid = await register(client, db, 'overview-owner@example.com', ('python', 'javascript'))
    other_headers, other_uid = await register(client, db, 'overview-other@example.com', ('python',))
    db.add_all([
        LearningEvent(user_id=uid, language='python', problem_id='two-sum', kind='solved'),
        LearningEvent(user_id=uid, language='javascript', problem_id='two-sum', kind='solved'),
        StudentPathRecord(user_id=uid, section='dsa', language='python', kind='goal',
                          body='Understand invariants', curriculum_version=1),
        StudentPathRecord(user_id=other_uid, section='dsa', language='python', kind='goal',
                          body='Other student', curriculum_version=1),
    ])
    await db.commit()
    response = await client.get('/study/profile-overview', headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert [row['language'] for row in data['languages']] == ['javascript', 'python']
    assert [next(s for s in row['sections'] if s['id'] == 'dsa')['completed']
            for row in data['languages']] == [1, 1]
    assert data['student_records']['dsa'] == {'goal': 1}
    assert data['student_records']['design-patterns'] == {}
    for row in data['languages']:
        assert {s['id'] for s in row['sections']} == {'learning-path', 'dsa', 'design-patterns'}
        assert next(s for s in row['sections'] if s['id'] == 'learning-path')['metric'] == 'Current path checkpoints'
        assert next(s for s in row['sections'] if s['id'] == 'design-patterns')['completed'] is None
    assert (await client.get('/study/profile-overview', headers=other_headers)).json()['student_records']['dsa'] == {'goal': 1}
    assert (await client.get('/study/profile-overview')).status_code == 401


async def test_profile_overview_retains_record_counts_without_active_language(client, db):
    account = (await client.post('/auth/register', json={
        'email': 'overview-expired@example.com', 'password': 'password123'})).json()
    uid = account['user']['id']
    headers = {'Authorization': 'Bearer ' + account['access_token']}
    db.add(StudentPathRecord(user_id=uid, section='language', language='javascript',
                             kind='goal', body='Old goal', curriculum_version=1))
    await db.commit()
    response = await client.get('/study/profile-overview', headers=headers)
    assert response.status_code == 200
    assert response.json()['languages'] == []
    assert response.json()['student_records']['language'] == {'goal': 1}
    user = await db.get(User, uid)
    user.status = 'suspended'
    await db.commit()
    assert (await client.get('/study/profile-overview', headers=headers)).status_code == 403
