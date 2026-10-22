from app.db.models import DebugChallengeAttempt, LearningEvent
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
