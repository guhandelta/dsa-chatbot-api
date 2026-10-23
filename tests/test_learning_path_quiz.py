"""Curriculum model (shared spine, depth modules, mastery) and the quiz engine."""
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import LearningEvent, QuizAnswer, QuizSession, SecurityEvent, User
from app.services import learning_path as lp
from app.services import quiz


@pytest.fixture
def unauthored_go(monkeypatch):
    """Go as it was before any stage files or quiz bank were authored."""
    from app.services import content_catalog, quiz as quiz_module
    find_path, bank_version = content_catalog.find_path, quiz_module._bank_version
    monkeypatch.setattr(content_catalog, 'find_path',
                        lambda cid: None if cid.startswith('go-path-') else find_path(cid))
    monkeypatch.setattr(quiz_module, '_bank_version', lambda language: (
        (str(quiz_module.BANK_DIR / 'go.json'), 0) if language == 'go' else bank_version(language)))


async def make_user(db, email='path@example.com'):
    user = User(email=email, hashed_password='x', peppercorns=50)
    db.add(user)
    await db.flush()
    return user


def item(language, item_id):
    return quiz.items(language)[item_id]


# ---------------------------------------------------------------- learning path

def test_shared_spine_has_twelve_stages_on_the_l1_l2_l3_ladder():
    assert [s.number for s in lp.SPINE] == list(range(1, 13))
    assert [s.level for s in lp.SPINE] == ['L1'] * 6 + ['L2'] * 4 + ['L3'] * 2
    assert all(lp.DEPTH_MODULES[lang] for lang in lp.LANGUAGE_LABELS)


def test_python_path_reuses_stage_files_and_branches_into_depth_modules():
    nodes = lp.nodes('python')
    stages = [n for n in nodes if n['kind'] == 'stage']
    modules = [n for n in nodes if n['kind'] == 'module']
    assert [n['exercise_id'] for n in stages][:2] == ['python-path-01-values', 'python-path-02-conditions']
    assert all(n['lesson_ids'][-1] == 'python-fundamentals' for n in stages)
    assert [n['order'] for n in modules] == list(range(13, 13 + len(lp.DEPTH_MODULES['python'])))
    assert modules[0]['lesson_sources'][0]['id'].startswith('ref-')
    assert all(n['checks_available'] > 0 for n in stages)
    assert lp.find_node('python', 'python:stage-07')['title'] == 'Maps and frequency counting'
    assert lp.find_node('python', 'python:stage-99') is None


def test_languages_without_stage_files_still_get_a_path(unauthored_go):
    stages = [n for n in lp.nodes('go') if n['kind'] == 'stage']
    assert len(stages) == 12 and not any(n['exercise_id'] for n in stages)
    assert stages[0]['lesson_ids'] == ['go-fundamentals']


def test_practice_set_matches_the_learners_level(monkeypatch):
    stage = lp.SPINE[0]
    assert {p['difficulty'] for p in lp.practice_set(stage)} == {'Easy'}
    stretch = lp.practice_set(stage, 'L2')
    assert {'id': 'sum-of-two-integers', 'title': 'Sum of Two Integers (LC 371)', 'difficulty': 'Medium',
            'role': 'stretch'} in stretch
    assert all(p['role'] == 'apply' for p in stretch if p['difficulty'] == 'Easy')
    ghost = lp.Stage(1, 'values', 'Values', 'L1', (), ('no-such-problem', 'two-sum'))
    assert [p['id'] for p in lp.practice_set(ghost)] == ['two-sum']


def test_module_sources_are_capped_and_answer_free():
    sources = lp.module_sources('c', lp.Module('pointers', 'Pointers', 'L3', ('pointer',)))
    assert 1 <= len(sources) <= 4
    assert lp.module_sources('python', lp.Module('none', 'None', 'L3', ('zzzz-not-a-topic',))) == []


def test_node_for_exercise_maps_a_stage_file_back_to_its_language():
    assert lp.node_for_exercise('python-path-07-maps') == ('python', lp.SPINE[6])
    assert lp.node_for_exercise('two-sum') is None


@pytest.mark.parametrize('language,runner,verdict', [
    ('python', True, 'launch-ready'), ('typescript', False, 'quiz-led'),
    ('c', True, 'launch-ready'), ('go', False, 'needs-authoring'),
])
def test_readiness_reflects_existing_content(monkeypatch, request, language, runner, verdict):
    if language == 'go':
        request.getfixturevalue('unauthored_go')
    monkeypatch.setattr('app.services.code_runner.available_languages',
                        lambda: {language: runner})
    report = lp.readiness(language)
    assert report['verdict'] == verdict and report['runner'] is runner
    assert report['spine_total'] == 12


async def test_progress_moves_the_learner_through_mastery(db):
    user = await make_user(db)
    fresh = await lp.progress(db, user.id, 'python')
    assert fresh['current_id'] == 'python:stage-01' and fresh['completed'] == 0
    assert next(n for n in fresh['nodes'] if n['id'] == 'python:module-typing')['status'] == 'not-started'
    db.add(LearningEvent(user_id=user.id, problem_id='python-path-01-values', kind='solved', language='python'))
    await db.flush()
    halfway = await lp.progress(db, user.id, 'python')
    assert halfway['nodes'][0]['status'] == 'in-progress' and halfway['current_id'] == 'python:stage-01'
    db.add(QuizSession(user_id=user.id, language='python', node_id='python:stage-01', total=3, answered=3,
                       score=2.0, completed_at=datetime.now(timezone.utc)))
    await db.flush()
    done = await lp.progress(db, user.id, 'python')
    assert done['nodes'][0]['complete'] and done['current_id'] == 'python:stage-02'
    assert done['completed_stages'] == [1]
    first = await lp.reward_completed_stages(db, user.id, 'python')
    assert [g['amount'] for g in first] == [settings.reward_stage_complete]
    assert await lp.reward_completed_stages(db, user.id, 'python') == []


async def test_a_low_quiz_score_does_not_master_the_node(db):
    user = await make_user(db, 'low@example.com')
    db.add(LearningEvent(user_id=user.id, problem_id='python-path-01-values', kind='solved', language='python'))
    db.add(QuizSession(user_id=user.id, language='python', node_id='python:stage-01', total=3, answered=3,
                       score=1.0, completed_at=datetime.now(timezone.utc)))
    await db.flush()
    node = (await lp.progress(db, user.id, 'python'))['nodes'][0]
    assert node['check_score'] == pytest.approx(1 / 3) and not node['complete']


async def test_a_language_without_assessments_keeps_unavailable_nodes_visible(db, monkeypatch, unauthored_go):
    user = await make_user(db, 'none@example.com')
    monkeypatch.setattr(lp, 'DEPTH_MODULES', {})
    state = await lp.progress(db, user.id, 'go')
    assert state['current_id'] == 'go:stage-01' and state['total'] == 12
    assert state['available_total'] == 0 and not state['curriculum_complete']


# ---------------------------------------------------------------- the bank

def test_authored_and_knowledge_base_items_are_both_used():
    python = quiz.items('python')
    assert {i['source'] for i in python.values()} == {'authored', 'knowledge-base'}
    assert {i['type'] for i in python.values()} == set(quiz.TYPES)
    assert {i['source'] for i in quiz.items('rust').values()} == {'authored'}


def test_public_view_never_contains_answer_keys_or_tests():
    for entry in quiz.items('python').values():
        view = quiz.public(entry)
        assert not {'answer', 'solution', 'tests', 'keywords', 'accept', 'explanation'} & view.keys()
    fix = quiz.public(item('python', 'py-s01-fix'))
    assert fix['function'] == 'average_minutes' and fix['test_count'] == 6 and fix['language'] == 'python'


def test_lesson_code_extracts_both_snippets_and_skips_rows_without_them():
    doc = 'Concept: x\nIncorrect:\nbad()\nCorrect:\ngood()\nComplexity: O(1)'
    assert quiz.lesson_code(doc) == '# Incorrect version\nbad()\n\n# Correct version\ngood()'
    assert quiz.lesson_code('Concept: only prose') == ''


def test_knowledge_base_rows_are_filtered_and_mapped(monkeypatch):
    def row(rid, kind='exercise', subject='python', answer='42', grading='exact', ds='array', prompt='What prints?',
            concept='c1'):
        payload = {'answer': answer, 'prompt': prompt, 'grading': grading, 'concept_id': concept}
        return {'id': rid, 'document': '', 'metadata': {'kind': kind, 'language': 'python', 'subject': subject,
                                                       'data_structure_id': ds, 'level': 'L1'},
                'payload': {'payload': payload}}
    concept = {'id': 'concept-row', 'document': 'Incorrect:\nx = 1\nCorrect:\nx = 2',
               'metadata': {'kind': 'concept', 'language': 'python', 'contains_answer': False},
               'payload': {'id': 'c1'}}
    rows = [concept, row('ok'), row('rubric', grading='rubric', concept='nope'),
            row('module', grading='judge', ds='zzz', prompt='Explain this generator', concept='nope'),
            row('loose', grading='rubric', ds='zzz', prompt='Explain', concept='nope'),
            row('no-code', concept='nope'), row('not-exercise', kind='concept'),
            row('embedded', subject='embedded-python'), row('no-answer', answer=None),
            row('list-grading', grading=['correct result'])]
    monkeypatch.setattr(quiz, '_kb_rows', lambda: iter(rows))
    out = {i['id']: i for i in quiz._knowledge_base('python', ('fake-version',))}
    assert set(out) == {'ok', 'rubric', 'module', 'loose'}
    assert out['ok']['type'] == 'short_answer' and out['ok']['node_id'] == 'python:stage-06'
    assert out['ok']['code'].startswith('# Incorrect version')
    assert out['rubric']['type'] == 'explain' and 'code' not in out['rubric']
    assert out['module']['node_id'] == 'python:module-iterators-generators'
    assert out['loose']['node_id'] is None


def test_draw_mixes_formats_and_puts_weak_concepts_first():
    candidates = quiz.pool('python', 'python:stage-06')
    drawn = quiz.draw(candidates, 4, seed='s')
    assert len({i['type'] for i in drawn}) == 4
    # Short quizzes rotate their starting format, so every format gets drawn.
    seen = {i['type'] for seed in range(30) for i in quiz.draw(candidates, 5, seed=str(seed))}
    assert seen == set(quiz.TYPES)
    assert len(quiz.draw(candidates, 50, seed='s')) == len(candidates)
    weak = quiz.draw(candidates, 1, weak={'list-multiplication'}, seed='s')
    assert weak[0]['concept'] == 'list-multiplication'


# ---------------------------------------------------------------- grading

async def test_multiple_choice_grading():
    mcq = item('python', 'py-s01-mcq')
    right = await quiz.grade(mcq, 1)
    assert right['correct'] and right['grading'] == 'choice' and right['expected'] == '7 // 2'
    assert not (await quiz.grade(mcq, '0'))['correct']
    for bad in ('x', 9):
        with pytest.raises(HTTPException) as err:
            await quiz.grade(mcq, bad)
        assert err.value.status_code == 422


async def test_short_answer_grading_normalises_but_stays_exact():
    short = item('python', 'py-s02-short')
    assert (await quiz.grade(short, '  "True   False". '))['correct']
    near = await quiz.grade(short, 'true false')
    assert not near['correct'] and 'capitalisation' in near['feedback']
    assert (await quiz.grade(short, 'False'))['feedback'] == 'That is not what it prints.'
    assert (await quiz.grade({**short, 'accept': ['T F']}, 'T F'))['correct']
    with pytest.raises(HTTPException):
        await quiz.grade(short, '   ')


async def test_explain_falls_back_to_keyword_rubric_without_a_model():
    explain = item('python', 'py-s06-explain')
    full = await quiz.grade(explain, 'values.sort() mutates the caller list in place; use sorted(values) or a copy via values[:].')
    assert full['correct'] and full['grading'] == 'keywords' and full['score'] == 1.0
    partial = await quiz.grade(explain, 'I would call sorted() on the input list first.')
    assert not partial['correct'] and 'also mentions' in partial['feedback']
    assert (await quiz.grade(explain, 'sorted'))['score'] == 0.0
    kb = {'type': 'explain', 'prompt': 'Why?', 'answer': 'Marking visited on enqueue prevents duplicates entering the queue.'}
    assert (await quiz.grade(kb, 'Because marking visited when you enqueue prevents duplicates in the queue'))['correct']


async def test_explain_uses_the_model_grader_when_available():
    class Judge:
        def __init__(self, content):
            self.content = content

        async def ainvoke(self, messages):
            assert '<student>' in messages[1].content
            return SimpleNamespace(content=self.content)

    explain = item('python', 'py-s04-explain')
    graded = await quiz.grade(explain, 'Defaults are created per call.', provider='openai',
                              model_factory=lambda _: Judge('Sure: {"score": 0.2, "feedback": "Defaults are evaluated once.", "misconception": "defaults are re-created per call"}'))
    assert graded['grading'] == 'rubric-model' and not graded['correct']
    assert graded['misconception'] == 'defaults are re-created per call'
    blocks = await quiz.grade(explain, 'Evaluated once and shared.', provider='openai',
                              model_factory=lambda _: Judge([{'text': '{"score": 3}'}, 'tail']))
    assert blocks['score'] == 1.0 and blocks['correct']
    broken = await quiz.grade(explain, 'Defaults are evaluated once at definition and shared; use None.',
                              provider='openai', model_factory=lambda _: Judge('no json here'))
    assert broken['grading'] == 'keywords'


def test_judge_provider_prefers_a_configured_provider(monkeypatch):
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: ['claude', 'openai'])
    assert quiz.judge_provider() == 'claude'
    monkeypatch.setattr('app.services.chat_model_routing.configured_providers', lambda: [])
    assert quiz.judge_provider() is None


async def test_code_items_are_graded_by_running_hidden_tests():
    fix = item('python', 'py-s01-fix')
    fixed = await quiz.grade(fix, fix['solution'])
    assert fixed['correct'] and fixed['tests']['passed'] == 6 and fixed['tests']['first_failure'] is None
    buggy = await quiz.grade(fix, fix['code'])
    assert not buggy['correct'] and buggy['tests']['first_failure']['case'] == 2  # 30.0 == 30 passes
    assert buggy['expected'] == fix['solution']
    crash = await quiz.grade(item('python', 'py-s01-write'), 'def seconds_to_minutes(seconds):\n    raise ValueError()')
    assert crash['tests']['first_failure']['got'] is None
    js = item('javascript', 'js-s12-fix')
    assert (await quiz.grade(js, js['solution']))['correct']


async def test_code_grading_reports_an_unavailable_runtime(monkeypatch):
    monkeypatch.setattr('app.services.code_runner.run_suite', lambda *a, **kw: {'results': []})
    result = await quiz.grade(item('python', 'py-s01-fix'), 'def average_minutes(t, d):\n    return t // d')
    assert result['tests']['status'] == 'unverified' and not result['correct']


def test_normalize():
    assert quiz.normalize(" 'a  b' ") == 'a b' and quiz.normalize('done.') == 'done'


# ---------------------------------------------------------------- sessions

async def test_quiz_session_lifecycle_records_answers_and_pays_stage_reward(db):
    user = await make_user(db, 'lifecycle@example.com')
    db.add(LearningEvent(user_id=user.id, problem_id='python-path-01-values', kind='solved', language='python'))
    await db.flush()
    started = await quiz.start(db, user, 'python', None, 3)
    assert started['node_id'] == 'python:stage-01' and started['total'] == 3
    assert not any('answer' in i for i in started['items'])
    by_id = quiz.items('python')
    for entry in started['items']:
        full = by_id[entry['id']]
        response = {'mcq': full.get('answer'), 'mcq_code': full.get('answer'), 'short_answer': full.get('answer'),
                    'fix_bug': full.get('solution'), 'write_snippet': full.get('solution'),
                    'explain': full.get('answer')}[full['type']]
        result = await quiz.answer(db, user, started['quiz_id'], entry['id'], response)
        assert result['correct'], (entry['id'], result)
    assert result['complete'] and [r['reason'] for r in result['rewards']] == ['earn:stage']
    summary = await quiz.summary(db, user, started['quiz_id'])
    assert summary['mastered'] and summary['correct'] == 3 and summary['weak_concepts'] == []
    assert (await quiz.best_scores(db, user.id, 'python')) == {'python:stage-01': 1.0}
    assert (await lp.progress(db, user.id, 'python'))['current_id'] == 'python:stage-02'


async def test_wrong_and_typed_answers_reveal_weak_spots(db):
    user = await make_user(db, 'weak@example.com')
    quiz_row = QuizSession(user_id=user.id, language='python', node_id='python:stage-04',
                           items_json=json.dumps(['py-s04-explain', 'py-s04-code']), total=2)
    db.add(quiz_row)
    await db.flush()
    typed = await quiz.answer(db, user, quiz_row.id, 'py-s04-explain', 'It is fine, each call gets a new list.')
    assert not typed['correct']
    await quiz.answer(db, user, quiz_row.id, 'py-s04-code', 0)
    weak = await quiz.weak_concepts(db, user.id, 'python')
    assert weak[0]['concept'] == 'mutable-default' and weak[0]['misses'] == 2
    seen = await quiz.insights(db, user.id, 'python')
    assert seen['responses'][0]['response'] == 'It is fine, each call gets a new list.'
    assert seen['responses'][0]['prompt'].startswith('Why is def log')
    assert (await quiz.summary(db, user, quiz_row.id))['weak_concepts'] == ['mutable-default']
    again = QuizSession(user_id=user.id, language='python', node_id='python:stage-04',
                        items_json=json.dumps(['py-s04-short']), total=1)
    db.add(again)
    await db.flush()
    await quiz.answer(db, user, again.id, 'py-s04-short', '6 15 4')
    assert (await quiz.weak_concepts(db, user.id, 'python'))[0]['misses'] == 2


async def test_start_rejects_unknown_nodes_and_empty_pools(db, unauthored_go, monkeypatch):
    user = await make_user(db, 'start@example.com')
    original_pool = quiz.pool
    monkeypatch.setattr(quiz, 'pool', lambda language, node: [] if node == 'python:module-typing' else original_pool(language, node))
    for node_id, status in (('python:stage-99', 404), ('python:module-typing', 409)):
        with pytest.raises(HTTPException) as err:
            await quiz.start(db, user, 'python', node_id, 3)
        assert err.value.status_code == status
    with pytest.raises(HTTPException) as err:
        await quiz.start(db, user, 'go', None, 3)
    assert err.value.status_code == 409 and 'Values and arithmetic' in err.value.detail


async def test_answer_guards(db, monkeypatch):
    user = await make_user(db, 'guards@example.com')
    other = await make_user(db, 'other@example.com')
    row = QuizSession(user_id=user.id, language='python', node_id='python:stage-01',
                      items_json=json.dumps(['py-s01-mcq', 'retired-item', 'py-s01-fix']), total=3)
    db.add(row)
    await db.flush()

    async def status(coro):
        with pytest.raises(HTTPException) as err:
            await coro
        return err.value.status_code

    assert await status(quiz.answer(db, other, row.id, 'py-s01-mcq', 1)) == 404
    assert await status(quiz.answer(db, user, 'missing', 'py-s01-mcq', 1)) == 404
    assert await status(quiz.answer(db, user, row.id, 'py-s02-mcq', 1)) == 404
    assert await status(quiz.answer(db, user, row.id, 'retired-item', 1)) == 410
    assert await status(quiz.answer(db, user, row.id, 'py-s01-mcq', 'x' * 20001)) == 422
    await quiz.answer(db, user, row.id, 'py-s01-mcq', 1)
    assert await status(quiz.answer(db, user, row.id, 'py-s01-mcq', 1)) == 409
    monkeypatch.setattr(settings, 'quiz_code_runs_per_hour', 0)
    assert await status(quiz.answer(db, user, row.id, 'py-s01-fix', 'def f(): pass')) == 429
    monkeypatch.setattr(settings, 'quiz_answers_per_hour', 1)
    assert await status(quiz.answer(db, user, row.id, 'py-s01-fix', 'def f(): pass')) == 429


async def test_answer_loses_a_concurrent_duplicate(db, monkeypatch):
    user = await make_user(db, 'dupe@example.com')
    row = QuizSession(user_id=user.id, language='python', node_id='python:stage-01',
                      items_json=json.dumps(['py-s01-mcq']), total=1)
    db.add(row)
    await db.flush()
    db.add(QuizAnswer(quiz_id=row.id, user_id=user.id, item_id='py-s01-mcq', item_type='mcq'))
    await db.flush()
    real = db.scalar

    async def stale(statement):
        if 'quiz_answers.id' in str(statement):
            return None  # the duplicate check ran before the other answer committed
        return await real(statement)

    monkeypatch.setattr(db, 'scalar', stale)
    with pytest.raises(HTTPException) as err:
        await quiz.answer(db, user, row.id, 'py-s01-mcq', 1)
    assert err.value.status_code == 409


async def test_blocked_code_records_a_security_event_and_is_not_run(db):
    user = await make_user(db, 'blocked@example.com')
    row = QuizSession(user_id=user.id, language='python', node_id='python:stage-01',
                      items_json=json.dumps(['py-s01-fix']), total=1)
    db.add(row)
    await db.flush()
    with pytest.raises(HTTPException) as err:
        await quiz.answer(db, user, row.id, 'py-s01-fix', 'import socket\ndef average_minutes(t, d):\n    return 0')
    assert err.value.status_code in (400, 403)
    assert await db.scalar(select(func.count()).select_from(SecurityEvent).where(SecurityEvent.user_id == user.id)) == 1
    assert await db.scalar(select(func.count()).select_from(QuizAnswer).where(QuizAnswer.quiz_id == row.id)) == 0


async def test_profile_export_and_delete_cover_quiz_answers(client, db, subscribe_user):
    body = (await client.post('/auth/register', json={'email': 'export@example.com', 'password': 'password123'})).json()
    headers = {'Authorization': 'Bearer ' + body['access_token']}
    uid = body['user']['id']
    row = QuizSession(user_id=uid, language='python', node_id='python:stage-01', total=1, answered=1)
    db.add(row)
    await db.flush()
    db.add(QuizAnswer(quiz_id=row.id, user_id=uid, item_id='py-s01-explain', item_type='explain',
                      response='my own words'))
    await db.commit()
    exported = (await client.get('/mentor/profile/export', headers=headers)).json()
    assert exported['quiz_answers'][0]['response'] == 'my own words'
    assert (await client.delete('/mentor/profile', headers=headers)).status_code == 200
    assert await db.scalar(select(func.count()).select_from(QuizAnswer).where(QuizAnswer.user_id == uid)) == 0
    assert await db.scalar(select(func.count()).select_from(QuizSession).where(QuizSession.user_id == uid)) == 0


async def test_a_quiz_answer_can_complete_a_streak(db, monkeypatch):
    from datetime import timedelta
    user = await make_user(db, 'streaky@example.com')
    monkeypatch.setattr(settings, 'reward_streak_days', 2)
    db.add(LearningEvent(user_id=user.id, problem_id='two-sum', kind='attempt', language='python',
                         created_at=datetime.now(timezone.utc) - timedelta(days=1)))
    row = QuizSession(user_id=user.id, language='python', node_id='python:stage-01',
                      items_json=json.dumps(['py-s01-mcq', 'py-s01-code']), total=2)
    db.add(row)
    await db.flush()
    result = await quiz.answer(db, user, row.id, 'py-s01-mcq', 1)
    assert [r['reason'] for r in result['rewards']] == ['earn:streak'] and not result['complete']


@pytest.mark.parametrize('node_id,level', [('python:stage-06', 'L1'),
                                         ('python:module-asyncio', 'L4')])
def test_pool_filters_levels_without_remapping_or_mutating_items(monkeypatch, node_id, level):
    bank = {}
    for source in ('authored', 'knowledge-base'):
        for value in ('L0', 'L1', 'L2', 'L3', 'L4', None, 'unknown'):
            key = f'{source}-{value}'
            bank[key] = {'id': key, 'node_id': node_id, 'source': source, 'level': value}
    bank['other'] = {'id': 'other', 'node_id': 'python:stage-01', 'level': 'L0', 'source': 'authored'}
    monkeypatch.setattr(quiz, 'items', lambda language: bank)
    selected = quiz.pool('python', node_id)
    expected = {key for key, entry in bank.items() if entry['node_id'] == node_id and
                ((entry['level'] in lp.LEVEL_LABELS and entry['level'] <= level) or
                 (entry['source'] == 'authored' and entry['level'] not in lp.LEVEL_LABELS))}
    assert {entry['id'] for entry in selected} == expected
    assert all(entry['node_id'] == node_id and entry['level'] <= level for entry in selected)
    assert next(entry for entry in selected if entry['id'] == 'authored-unknown')['level'] == level
    assert bank['authored-unknown']['level'] == 'unknown'
    assert quiz.pool_size('python', {'id': node_id}) == len(selected)
    assert quiz.pool('python', 'python:stage-99') == []


def test_coverage_requires_stage_content_and_each_module_assessment(monkeypatch):
    monkeypatch.setattr(lp, 'stage_exercise_id', lambda language, stage: None)
    monkeypatch.setattr(lp, '_quiz_count', lambda language, node: 1 if node['order'] == 1 else 0)
    monkeypatch.setattr(lp, 'module_sources', lambda *args: [{'id': 'reference', 'title': 'Reference'}])
    monkeypatch.setattr('app.services.code_runner.available_languages', lambda: {'python': True})
    path = lp.nodes('python')
    assert path[0]['lesson_ids'] == ['python-fundamentals']
    assert path[0]['missing_content'] == ['stage_lesson', 'exercise']
    assert path[1]['missing_content'] == ['stage_lesson', 'exercise', 'checks']
    assert path[-1]['missing_content'] == ['module_assessment']
    report = lp.readiness('python')
    assert not report['coverage_ready'] and report['verdict'] != 'launch-ready'
    assert report['spine_checks'] == 1 and report['depth_assessments'] == 0
    assert len(report['missing_content']) == len(path)


async def test_exhausted_available_work_does_not_complete_missing_curriculum(db, monkeypatch):
    user = await make_user(db, 'partial@example.com')
    monkeypatch.setattr(lp, '_quiz_count', lambda language, node: 1 if node['order'] == 1 else 0)
    monkeypatch.setattr(lp, 'stage_exercise_id', lambda *args: None)
    db.add(QuizSession(user_id=user.id, language='python', node_id='python:stage-01', total=1,
                       answered=1, score=1, completed_at=datetime.now(timezone.utc)))
    await db.flush()
    state = await lp.progress(db, user.id, 'python')
    assert state['completed'] == 0 and state['available_total'] == 1
    assert state['nodes'][0]['assessment_passed'] and not state['nodes'][0]['mastered']
    assert state['total'] == len(state['nodes']) > state['completed']
    assert state['current_id'] == 'python:stage-01'
    assert not state['curriculum_complete'] and not state['coverage_ready']


async def test_start_rejects_a_pool_containing_only_advanced_checks(db, monkeypatch):
    user = await make_user(db, 'advanced@example.com')
    monkeypatch.setattr(quiz, 'items', lambda language: {'advanced': {
        'id': 'advanced', 'node_id': 'python:stage-01', 'level': 'L4', 'source': 'knowledge-base'}})
    with pytest.raises(HTTPException) as error:
        await quiz.start(db, user, 'python', 'python:stage-01', 3)
    assert error.value.status_code == 409


def test_public_authored_level_inference_is_consistent_for_session_replay():
    entry = {**item('python', 'py-s01-mcq'), 'level': 'unknown'}
    assert quiz.public(entry)['level'] == 'L1'
    assert entry['level'] == 'unknown'
    assert quiz.public({**entry, 'level': 'L0'})['level'] == 'L0'


def test_launch_ready_requires_coverage_at_every_node(monkeypatch):
    monkeypatch.setattr(lp, 'stage_exercise_id', lambda language, stage: f'exercise-{stage.number}')
    monkeypatch.setattr(lp, '_quiz_count', lambda *args: 3)
    monkeypatch.setattr(lp, 'module_sources', lambda *args: [{'id': 'reference', 'title': 'Reference'}])
    monkeypatch.setattr('app.services.code_runner.available_languages', lambda: {'python': True})
    report = lp.readiness('python')
    assert report['coverage_ready'] and report['verdict'] == 'launch-ready'
    assert report['missing_content'] == []
    assert report['spine_checks'] == 12
    assert report['depth_assessments'] == report['depth_total']


@pytest.mark.parametrize('language', ['c', 'typescript'])
async def test_quiz_only_stage_never_masters_or_pays_stage_reward(db, language, monkeypatch):
    from app.db.models import Transaction
    # Both languages now ship stage files; simulate a stage that has checks only.
    monkeypatch.setattr(lp, 'stage_exercise_id', lambda language, stage: None)
    user = await make_user(db, f'quiz-only-{language}@example.com')
    node = lp.find_node(language, f'{language}:stage-01')
    assert node['checks_available'] > 0 and node['exercise_id'] is None
    assert 'stage_lesson' in node['missing_content'] and 'exercise' in node['missing_content']
    started = await quiz.start(db, user, language, node['id'], 1)
    full = quiz.items(language)[started['items'][0]['id']]
    response = full['answer'] if 'answer' in full else full['solution']
    result = await quiz.answer(db, user, started['quiz_id'], full['id'], response)
    assert result['correct'] and result['complete']
    assert not any(reward['reason'] == 'earn:stage' for reward in result['rewards'])
    state = await lp.progress(db, user.id, language)
    stage = state['nodes'][0]
    assert stage['checks_passed'] and stage['assessment_passed']
    assert not stage['complete'] and not stage['mastered']
    assert state['completed'] == 0 and state['completed_stages'] == []
    assert state['current_id'] == node['id']
    assert await lp.reward_completed_stages(db, user.id, language) == []
    assert await db.scalar(select(func.count()).select_from(Transaction).where(
        Transaction.user_id == user.id, Transaction.reason == 'earn:stage')) == 0
    summary = await quiz.summary(db, user, started['quiz_id'])
    assert summary['complete'] and summary['assessment_passed'] and not summary['mastered']


@pytest.mark.parametrize('has_lesson', [False, True])
async def test_module_mastery_requires_a_lesson_and_passed_checks(db, monkeypatch, has_lesson):
    user = await make_user(db, f'module-coverage-{has_lesson}@example.com')
    monkeypatch.setattr(lp, 'module_sources', lambda *args: [{'id': 'lesson', 'title': 'Lesson'}] if has_lesson else [])
    monkeypatch.setattr(lp, '_quiz_count', lambda *args: 3)
    node_id = 'python:module-typing'
    db.add(QuizSession(user_id=user.id, language='python', node_id=node_id, total=3,
                       answered=3, score=2, completed_at=datetime.now(timezone.utc)))
    await db.flush()
    state = await lp.progress(db, user.id, 'python')
    node = next(n for n in state['nodes'] if n['id'] == node_id)
    assert node['checks_passed'] and node['assessment_passed']
    assert node['complete'] is has_lesson and node['mastered'] is has_lesson
    assert node['coverage_ready'] is has_lesson


async def test_evidence_is_the_learners_own_passing_code_per_concept(db, monkeypatch):
    monkeypatch.setattr(quiz, 'judge_provider', lambda: None)
    user = await make_user(db, 'evidence@example.com')
    node = next(n for n in lp.nodes('c') if any(i['type'] == 'fix_bug' for i in quiz.pool('c', n['id'])))
    started = await quiz.start(db, user, 'c', node['id'], len(quiz.pool('c', node['id'])))
    code_item = next(quiz.items('c')[i['id']] for i in started['items'] if i['type'] == 'fix_bug')
    fixed = code_item['solution']
    await quiz.answer(db, user, started['quiz_id'], code_item['id'], fixed)
    rows = await quiz.evidence(db, user.id, 'c')
    assert len(rows) == 1 and rows[0]['code'] == fixed and rows[0]['concept'] == code_item['concept']
    assert 'answer' not in rows[0] and 'expected' not in rows[0] and 'solution' not in rows[0]
    assert all(r['code'] != '' for r in rows)
    assert await quiz.evidence(db, user.id, 'python') == []


async def test_a_wrong_code_answer_is_not_evidence(db, monkeypatch):
    monkeypatch.setattr(quiz, 'judge_provider', lambda: None)
    user = await make_user(db, 'wrong-evidence@example.com')
    node = next(n for n in lp.nodes('c') if any(i['type'] == 'fix_bug' for i in quiz.pool('c', n['id'])))
    started = await quiz.start(db, user, 'c', node['id'], len(quiz.pool('c', node['id'])))
    code_item = next(quiz.items('c')[i['id']] for i in started['items'] if i['type'] == 'fix_bug')
    await quiz.answer(db, user, started['quiz_id'], code_item['id'], code_item['code'])
    assert await quiz.evidence(db, user.id, 'c') == []
