"""Study Room API: path-aware modes, daily free pool, quizzes and next steps."""
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select, update

from app.core.config import settings
from app.db.models import ChatThread, LearningEvent, QuizSession, StudyNote, Subscription, Transaction, User
from app.services import study_room
from app.services.study_room import guard_socratic, split_takeaway

TAKEAWAY = ("A dict maps keys to values.\n\nTAKEAWAY\nConcept: Use get for a default.\n"
            "Example: counts.get(w, 0)\nPitfall: counts[w] += 1 raises KeyError.")


class FakeModel:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return SimpleNamespace(content=self.replies.pop(0) if len(self.replies) > 1 else self.replies[0])


@pytest.fixture
def model(monkeypatch):
    fake = FakeModel([TAKEAWAY])
    monkeypatch.setattr('app.services.llm_router.get_llm', lambda provider: fake)
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: ['openai'])
    monkeypatch.setattr('app.services.knowledge_base.get_vectorstore',
                        lambda: SimpleNamespace(similarity_search=lambda *a, **kw: []))
    return fake


async def register(client, db, email='study@example.com', languages=('python', 'javascript')):
    body = (await client.post('/auth/register', json={'email': email, 'password': 'password123'})).json()
    for language in languages:
        db.add(Subscription(user_id=body['user']['id'], language=language,
                            expires_at=datetime.now(timezone.utc) + timedelta(days=42)))
    await db.commit()
    return {'Authorization': 'Bearer ' + body['access_token']}, body['user']['id']


def ask(**overrides):
    return {'language': 'python', 'mode': 'explain', 'message': 'Why does my dict lookup fail?', **overrides}


# ---------------------------------------------------------------- path

async def test_readiness_lists_every_language(client, db):
    headers, _ = await register(client, db)
    body = (await client.get('/study/readiness', headers=headers)).json()
    verdicts = {r['language']: r['verdict'] for r in body['languages']}
    assert verdicts['python'] == verdicts['java'] == verdicts['javascript'] == 'next-wave'
    assert verdicts['typescript'] == verdicts['ruby'] == 'quiz-led'
    assert body['levels']['L4'] == 'Language mastery'


async def test_path_lesson_and_access(client, db):
    headers, _ = await register(client, db)
    path = (await client.get('/study/path', headers=headers, params={'language': 'python'})).json()
    assert path['current_id'] == 'python:stage-01' and path['label'] == 'Python'
    assert path['readiness']['verdict'] == 'next-wave' and len(path['nodes']) == 20
    assert (await client.get('/study/path', headers=headers, params={'language': 'rust'})).status_code == 403
    stage = (await client.get('/study/nodes/python:stage-07/lesson', headers=headers,
                              params={'language': 'python'})).json()
    assert '## Learn' in stage['markdown'] and '## Solutions' not in stage['markdown']
    assert 'test_cases' not in stage['markdown']
    module = (await client.get('/study/nodes/python:module-iterators-generators/lesson', headers=headers,
                               params={'language': 'python'})).json()
    assert module['markdown'].startswith('## Iterators generators and exhaustion')
    missing = await client.get('/study/nodes/python:stage-99/lesson', headers=headers, params={'language': 'python'})
    assert missing.status_code == 404


# ---------------------------------------------------------------- explain + pricing

async def test_explain_returns_a_takeaway_card_and_uses_the_free_pool(client, db, model, monkeypatch):
    headers, uid = await register(client, db)
    assert (await client.get('/study/allowance', headers=headers)).json() == {
        'daily_free': 5, 'used_today': 0, 'free_left': 5, 'cost_after_free': 1}
    r = await client.post('/study/message', headers=headers, json=ask())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['answer'] == 'A dict maps keys to values.'
    assert body['takeaway'] == {'concept': 'Use get for a default.', 'example': 'counts.get(w, 0)',
                                'pitfall': 'counts[w] += 1 raises KeyError.'}
    assert body['focus'] == {'kind': 'node', 'id': 'python:stage-01', 'title': 'Values and arithmetic', 'auto': True}
    assert body['peppercorns_charged'] == 0 and body['peppercorns_remaining'] == settings.signup_bonus
    assert body['allowance']['free_left'] == 4
    system = model.calls[0][0].content
    assert 'Values and arithmetic' in system and '## Learn' in system and 'test_cases' not in system
    notes = (await client.get('/study/notes', headers=headers, params={'language': 'python'})).json()['notes']
    assert notes[0]['mode'] == 'explain' and notes[0]['node_id'] == 'python:stage-01'

    follow = await client.post('/study/message', headers=headers, json=ask(thread_id=body['thread_id']))
    assert follow.status_code == 200 and len(model.calls[1]) == 4  # system, prior pair, new question
    monkeypatch.setattr(settings, 'study_daily_free_messages', 2)
    paid = await client.post('/study/message', headers=headers, json=ask(message='And Counter?'))
    assert paid.json()['peppercorns_charged'] == 1
    assert paid.json()['peppercorns_remaining'] == settings.signup_bonus - 1
    assert paid.json()['allowance'] == {'daily_free': 2, 'used_today': 2, 'free_left': 0, 'cost_after_free': 1}


async def test_explain_without_a_takeaway_saves_no_note_and_honours_focus(client, db, model):
    model.replies = ['Plain answer.']
    headers, _ = await register(client, db, 'focus@example.com')
    r = await client.post('/study/message', headers=headers, json=ask(focus_id='two-sum'))
    assert r.json()['focus'] == {'kind': 'problem', 'id': 'two-sum', 'title': 'Two Sum (LC 1)', 'auto': False}
    assert r.json()['note_id'] is None and 'takeaway' not in r.json()
    node = await client.post('/study/message', headers=headers, json=ask(focus_id='python:module-dataclasses'))
    assert node.json()['focus']['id'] == 'python:module-dataclasses'
    missing = await client.post('/study/message', headers=headers, json=ask(focus_id='nope-not-here'))
    assert missing.status_code == 404


async def test_thread_guards(client, db, model):
    headers, _ = await register(client, db, 'threads@example.com')
    first = (await client.post('/study/message', headers=headers, json=ask())).json()
    wrong_mode = await client.post('/study/message', headers=headers, json=ask(
        mode='compare', compare_language='javascript', thread_id=first['thread_id']))
    assert wrong_mode.status_code == 409
    other, _ = await register(client, db, 'other-threads@example.com')
    stolen = await client.post('/study/message', headers=other, json=ask(thread_id=first['thread_id']))
    assert stolen.status_code == 404


async def test_receipts_replay_without_charging_twice(client, db, model):
    headers, uid = await register(client, db, 'replay@example.com')
    keyed = {**headers, 'Idempotency-Key': 'same'}
    first = await client.post('/study/message', headers=keyed, json=ask())
    again = await client.post('/study/message', headers=keyed, json=ask())
    assert first.json()['thread_id'] == again.json()['thread_id']
    assert len(model.calls) == 1
    assert (await client.get('/study/allowance', headers=headers)).json()['used_today'] == 1


async def test_unavailable_tutor_and_rate_limits_cost_nothing(client, db, model, monkeypatch):
    headers, uid = await register(client, db, 'limits@example.com')
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: [])
    assert (await client.post('/study/message', headers=headers, json=ask())).status_code == 503
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: ['openai'])
    monkeypatch.setattr(settings, 'chats_per_hour', 1)
    assert (await client.post('/study/message', headers=headers, json=ask())).status_code == 200
    limited = await client.post('/study/message', headers=headers, json=ask(message='again'))
    assert limited.status_code == 429 and 'chat turns' in limited.json()['detail']
    assert (await client.get('/auth/me', headers=headers)).json()['peppercorns'] == settings.signup_bonus


async def test_failed_generation_returns_the_free_use(client, db, monkeypatch):
    class Broken:
        async def ainvoke(self, messages):
            raise RuntimeError('provider down')
    monkeypatch.setattr('app.services.llm_router.get_llm', lambda provider: Broken())
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: ['openai'])
    headers, uid = await register(client, db, 'broken@example.com')
    assert (await client.post('/study/message', headers=headers, json=ask())).status_code == 502
    assert (await client.get('/study/allowance', headers=headers)).json()['free_left'] == 5


async def test_staff_may_choose_a_provider(client, db, model):
    headers, uid = await register(client, db, 'staff@example.com')
    await db.execute(update(User).where(User.id == uid).values(role='admin'))
    await db.commit()
    r = await client.post('/study/message', headers=headers, json=ask(provider='openai'))
    assert r.json()['model_routing']['strategy'] == 'manual'


async def test_suspended_accounts_cannot_study(client, db, model):
    headers, uid = await register(client, db, 'suspended@example.com')
    await db.execute(update(User).where(User.id == uid).values(status='suspended'))
    await db.commit()
    assert (await client.post('/study/message', headers=headers, json=ask())).status_code == 403
    assert (await client.post('/study/quiz', headers=headers, json={'language': 'python'})).status_code == 403


# ---------------------------------------------------------------- debug

async def test_debug_climbs_the_tier_ladder_and_never_returns_code(client, db, model):
    headers, _ = await register(client, db, 'debug@example.com')
    payload = ask(mode='debug', message='I think the loop is wrong', code='for i in range(n): total += i',
                  error='sum_to(3) returned 3, expected 6')
    assert (await client.post('/study/message', headers=headers, json={**payload, 'code': ''})).status_code == 422
    model.replies = ['What does range(n) produce when n is 3?', '```python\nfor i in range(1, n + 1):```']
    first = (await client.post('/study/message', headers=headers, json=payload)).json()
    assert first['hint_tier'] == 1 and first['tier_label'] == 'Orient'
    assert first['answer'] == 'What does range(n) produce when n is 3?'
    assert 'tier 1 (Orient)' in model.calls[0][0].content and 'returned 3' in model.calls[0][-1].content
    second = (await client.post('/study/message', headers=headers, json={**payload, 'thread_id': first['thread_id']})).json()
    assert second['hint_tier'] == 2 and '```' not in second['answer'] and second['answer'].endswith('?')
    resolved = await client.post('/study/debug/resolve', headers=headers,
                                 json={'thread_id': first['thread_id'], 'fix': 'range(n) stops before n; use range(1, n + 1).'})
    assert resolved.status_code == 200
    assert resolved.json()['body']['my_fix'].startswith('range(n)')
    assert 'I think the loop is wrong' in resolved.json()['body']['what_i_thought']
    explain_thread = (await client.post('/study/message', headers=headers, json=ask())).json()['thread_id']
    wrong = await client.post('/study/debug/resolve', headers=headers, json={'thread_id': explain_thread, 'fix': 'x'})
    assert wrong.status_code == 404


def test_socratic_guard_and_tier_helpers():
    for tier in (1, 2, 3, 4):
        held = guard_socratic('def fix():\n    return 1', tier, 'IndexError: list index out of range')
        assert held.endswith('?') and 'def ' not in held
    assert 'this result' in guard_socratic('No question here.', 4, '')
    assert guard_socratic('Why?', 1, 'e') == 'Why?'
    assert [study_room.debug_tier(n) for n in (0, 1, 5)] == [1, 2, 4]


def test_split_takeaway_and_text_blocks():
    assert split_takeaway('Just text') == ('Just text', None)
    assert split_takeaway(TAKEAWAY)[1]['pitfall'] == 'counts[w] += 1 raises KeyError.'
    assert study_room._text([{'text': 'a'}, 'b']) == 'ab' and study_room._text('c') == 'c'


# ---------------------------------------------------------------- compare

async def test_compare_needs_two_languages_and_saves_a_side_by_side_note(client, db, model):
    headers, _ = await register(client, db, 'compare@example.com')
    base = ask(mode='compare', message='How do maps handle a missing key?')
    assert (await client.post('/study/message', headers=headers, json=base)).status_code == 422
    assert (await client.post('/study/message', headers=headers, json={**base, 'compare_language': 'python'})).status_code == 422
    assert (await client.post('/study/message', headers=headers, json={**base, 'compare_language': 'rust'})).status_code == 403
    model.replies = ['| Aspect | python | javascript |\n|---|---|---|\n| syntax | d[k] | m.get(k) |\nWatch out: undefined.']
    r = await client.post('/study/message', headers=headers, json={**base, 'compare_language': 'javascript'})
    assert r.status_code == 200, r.text
    system = model.calls[0][0].content
    assert '<python_reference>' in system and '<javascript_reference>' in system
    note = (await client.get('/study/notes', headers=headers, params={'language': 'python'})).json()['notes'][0]
    assert note['mode'] == 'compare' and note['body']['second'] == 'javascript'
    assert note['body']['comparison'].startswith('| Aspect')


def test_compare_context_leads_with_both_lessons_for_a_shared_stage():
    from app.services import learning_path
    focus = {'kind': 'node', 'node': learning_path.find_node('python', 'python:stage-06')}
    first, second = study_room.compare_context('python', 'javascript', 'copy a list', focus)
    assert first.startswith('# Python: Lists') and second.startswith('# JavaScript: Arrays')
    module = {'kind': 'node', 'node': learning_path.find_node('python', 'python:module-dataclasses')}
    assert not study_room.compare_context('python', 'javascript', 'copy a list', module)[0].startswith('#')


def test_compare_context_matches_the_same_concept_family():
    first, second = study_room.compare_context('java', 'javascript', 'map getOrDefault missing key default value')
    assert first.startswith('Java') and second.startswith('JavaScript')
    assert 'No reference found' in study_room.compare_context('python', 'go', 'zzqx qqzz')[1]


# ---------------------------------------------------------------- what next

async def test_what_next_follows_progress_and_weak_spots(client, db):
    headers, uid = await register(client, db, 'next@example.com', ('python', 'go'))
    get = lambda lang='python': client.get('/study/next', headers=headers, params={'language': lang})
    first = (await get()).json()
    assert first['kind'] == 'quiz' and first['node_id'] == 'python:stage-01'
    assert first['title'] == 'Quick check: Values and arithmetic'
    db.add(QuizSession(user_id=uid, language='python', node_id='python:stage-01', total=3, answered=3,
                       score=3.0, completed_at=datetime.now(timezone.utc)))
    await db.commit()
    exercise = (await get()).json()
    assert exercise['kind'] == 'exercise' and exercise['link'] == {'to': '/practice', 'search': {'problem': 'python-path-01-values'}}
    db.add(LearningEvent(user_id=uid, problem_id='python-path-01-values', kind='solved', language='python'))
    db.add(QuizSession(user_id=uid, language='python', node_id='python:stage-02', total=3, answered=3,
                       score=0.0, completed_at=datetime.now(timezone.utc)))
    await db.commit()
    assert (await get()).json()['kind'] == 'exercise'  # checks tried, exercise still open
    db.add(LearningEvent(user_id=uid, problem_id='python-path-02-conditions', kind='solved', language='python'))
    await db.commit()
    checks = (await get()).json()
    assert checks['kind'] == 'quiz' and checks['node_id'] == 'python:stage-02' and '2 of 3' in checks['reason']
    go = (await get('go')).json()
    assert go['kind'] == 'content-gap' and go['status'] == 'blocked' and go['node_id'] == 'go:stage-01'


async def test_what_next_reviews_a_weak_concept_first(client, db, monkeypatch):
    monkeypatch.setattr("app.services.quiz.judge_provider", lambda: None)
    headers, uid = await register(client, db, 'weak-next@example.com')
    started = (await client.post('/study/quiz', headers=headers, json={'language': 'python', 'node_id': 'python:stage-06', 'count': 1})).json()
    await client.post(f"/study/quiz/{started['quiz_id']}/answer", headers=headers,
                      json={'item_id': started['items'][0]['id'], 'response': '0'})
    nxt = (await client.get('/study/next', headers=headers, params={'language': 'python'})).json()
    assert nxt['kind'] == 'quiz' and nxt['node_id'] == 'python:stage-06' and 'missed' in nxt['reason']
    assert nxt['title'] == 'Review quiz: Arrays and lists'


async def test_what_next_after_the_whole_path(db, monkeypatch):
    user = User(email='done@example.com', hashed_password='x')
    db.add(user)
    await db.flush()
    monkeypatch.setattr('app.services.learning_path.DEPTH_MODULES', {})
    for n in range(1, 13):
        db.add(LearningEvent(user_id=user.id, problem_id=f'python-path-{n:02d}-x', kind='solved', language='python'))
    real = study_room.learning_path.progress

    async def finished(session, user_id, language):
        state = await real(session, user_id, language)
        for node in state['nodes']:
            node.update(complete=True, coverage_ready=True, missing_content=[])
        return {**state, 'current_id': None}

    monkeypatch.setattr(study_room.learning_path, 'progress', finished)
    step = await study_room.recommend(db, user.id, 'python')
    assert step['kind'] == 'problem' and step['link']['to'] == '/practice'
    async def solved_everything(session, user_id, language):
        return {p['id'] for n in study_room.learning_path.nodes(language) for p in n['practice']}
    monkeypatch.setattr(study_room.learning_path, 'passed_exercises', solved_everything)
    assert (await study_room.recommend(db, user.id, 'python'))['kind'] == 'done'


async def test_a_node_without_graded_work_reports_a_content_blocker(db, monkeypatch):
    user = User(email='lesson@example.com', hashed_password='x')
    db.add(user)
    await db.flush()
    real = study_room.learning_path.progress

    async def lesson_only(session, user_id, language):
        state = await real(session, user_id, language)
        state['nodes'][0].update(exercise_id=None, checks_available=0,
                                 missing_content=['exercise', 'checks'], coverage_ready=False)
        return state

    monkeypatch.setattr(study_room.learning_path, 'progress', lesson_only)
    step = await study_room.recommend(db, user.id, 'python')
    assert step['kind'] == 'content-gap' and step['status'] == 'blocked'
    assert step['missing_content'] == ['exercise', 'checks'] and step['link'] is None


async def test_focus_keeps_unavailable_curriculum_visible(db):
    focus = await study_room.resolve_focus(db, 'nobody', 'go', None)
    assert focus['kind'] == 'node' and focus['id'] == 'go:stage-01'
    assert not focus['node']['coverage_ready']
    assert study_room.focus_context('go', focus, 'slice map')


def test_module_lesson_skips_rows_that_are_no_longer_eligible(monkeypatch):
    node = {'kind': 'module', 'lesson_sources': [{'id': 'gone', 'title': 'Gone'}]}
    assert study_room.lesson_markdown('python', node) == ''
    assert study_room.lesson_markdown('go', {'kind': 'stage', 'lesson_ids': []}) == ''


# ---------------------------------------------------------------- quiz + insights over HTTP

async def test_quiz_endpoints_grade_every_format(client, db, monkeypatch):
    from app.services import quiz
    # Exercise the local rubric; provider grading has its own isolated tests.
    monkeypatch.setattr(quiz, 'judge_provider', lambda: None)
    headers, uid = await register(client, db, 'quiz@example.com')
    started = await client.post('/study/quiz', headers=headers, json={'language': 'python', 'node_id': 'python:stage-06', 'count': 6})
    assert started.status_code == 200, started.text
    body = started.json()
    assert {i['type'] for i in body['items']} == set(quiz.TYPES)
    for entry in body['items']:
        full = quiz.items('python')[entry['id']]
        response = full.get('solution') or full.get('answer')
        r = await client.post(f"/study/quiz/{body['quiz_id']}/answer", headers=headers,
                              json={'item_id': entry['id'], 'response': response})
        assert r.status_code == 200 and r.json()['correct'], (entry['id'], r.text)
    summary = (await client.get(f"/study/quiz/{body['quiz_id']}", headers=headers)).json()
    assert summary['complete'] and summary['assessment_passed'] and summary['correct'] == 6
    assert not summary['mastered']  # the stage exercise still needs to pass
    insight = (await client.get('/study/insights', headers=headers, params={'language': 'python'})).json()
    assert insight['weak_concepts'] == [] and len(insight['responses']) == 2
    await db.execute(update(Subscription).where(Subscription.user_id == uid, Subscription.language == 'python')
                     .values(expires_at=datetime.now(timezone.utc) - timedelta(days=1)))
    await db.commit()
    assert (await client.get(f"/study/quiz/{body['quiz_id']}", headers=headers)).status_code == 403
    assert (await client.post(f"/study/quiz/{body['quiz_id']}/answer", headers=headers,
                              json={'item_id': body['items'][0]['id'], 'response': 1})).status_code == 403


async def test_free_pool_counts_refunds_back(db):
    user = User(email='pool@example.com', hashed_password='x')
    db.add(user)
    await db.flush()
    for reason in ('free:study', 'free:study', 'refund:free:study'):
        db.add(Transaction(user_id=user.id, amount=0, balance_after=0, reason=reason))
    db.add(Transaction(user_id=user.id, amount=0, balance_after=0, reason='free:study',
                       created_at=datetime.now(timezone.utc) - timedelta(days=1)))
    await db.flush()
    assert await study_room.free_used_today(db, user.id) == 1
    assert await study_room.message_price(db, user.id) == 0


async def test_missing_spine_blocks_advanced_work_and_weak_review(db, monkeypatch):
    from app.services import learning_path, quiz
    user = User(email='blocked-spine@example.com', hashed_password='x')
    db.add(user)
    await db.flush()
    monkeypatch.setattr(learning_path, 'stage_exercise_id', lambda *args: None)
    monkeypatch.setattr(learning_path, '_quiz_count', lambda language, node: 3)

    async def advanced_weak(*args, **kwargs):
        return [{'concept': 'advanced', 'misses': 2, 'correct': 0}]

    monkeypatch.setattr(quiz, 'weak_concepts', advanced_weak)
    db.add(QuizSession(user_id=user.id, language='python', node_id='python:stage-01',
                       total=3, answered=3, score=3, completed_at=datetime.now(timezone.utc)))
    await db.flush()
    state = await learning_path.progress(db, user.id, 'python')
    assert state['nodes'][0]['assessment_passed']
    assert not state['nodes'][0]['complete'] and not state['nodes'][0]['mastered']
    assert state['current_id'] == 'python:stage-01'
    step = await study_room.recommend(db, user.id, 'python')
    assert step['kind'] == 'content-gap' and step['status'] == 'blocked'
    assert step['node_id'] == 'python:stage-01'
    assert step['missing_content'] == ['stage_lesson', 'exercise']
    assert step['link'] is None


async def test_lessons_only_path_reports_content_gap_instead_of_done(db, monkeypatch):
    from app.services import learning_path
    monkeypatch.setattr(learning_path, 'stage_exercise_id', lambda *args: None)
    monkeypatch.setattr(learning_path, '_quiz_count', lambda *args: 0)
    step = await study_room.recommend(db, 'nobody', 'python')
    assert step['kind'] == 'content-gap' and step['node_id'] == 'python:stage-01'
    assert step['missing_content'] == ['stage_lesson', 'exercise', 'checks']
