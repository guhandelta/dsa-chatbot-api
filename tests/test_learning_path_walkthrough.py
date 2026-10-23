"""End-to-end walk of every learning path: a learner can read each lesson, pass each
check, finish each graded exercise, and reach the end of the curriculum with no
dead ends. Runs with the same sandbox the API uses for code items."""
import pytest
from sqlalchemy import select

from app.db.models import LearningEvent, QuizSession, User
from app.services import content_catalog, learning_path as lp, quiz, study_room


def correct_response(item):
    """What a learner who knows the material would submit for an item."""
    if item['type'] in ('mcq', 'mcq_code'):
        return item['answer']
    if item['type'] == 'short_answer':
        return item['answer']
    if item['type'] == 'explain':
        return item['answer']
    return item['solution']  # fix_bug / write_snippet: the reference solution


def runnable_here(language):
    from app.services.code_runner import available_languages
    return available_languages().get(language, False)


async def walk(db, language):
    user = User(email=f'walk-{language}@example.com', hashed_password='x', peppercorns=500)
    db.add(user)
    await db.flush()
    stuck = []
    for node in lp.nodes(language):
        nid = node['id']
        if not study_room.lesson_markdown(language, node).strip():
            stuck.append(f'{nid}: no lesson text')
        if node['kind'] == 'stage' and node['exercise_id']:
            if not content_catalog.find_path(node['exercise_id']):
                stuck.append(f'{nid}: exercise file missing')
            db.add(LearningEvent(user_id=user.id, problem_id=node['exercise_id'], kind='solved', language=language))
            await db.flush()
        if not node['checks_available']:
            stuck.append(f'{nid}: no checks')
            continue
        started = await quiz.start(db, user, language, nid, node['checks_available'])
        for public_item in started['items']:
            full = quiz.items(language)[public_item['id']]
            if full['type'] in quiz.CODE_TYPES and not runnable_here(language):
                stuck.append(f"{nid}: code check {full['id']} needs the {language} runner, which this machine lacks")
                continue
            result = await quiz.answer(db, user, started['quiz_id'], full['id'], correct_response(full))
            if not result['correct']:
                stuck.append(f"{nid}: correct answer marked wrong for {full['id']} ({full['type']}): {result.get('feedback', '')[:120]}")
        summary = await quiz.summary(db, user, started['quiz_id'])
        if not summary['assessment_passed']:
            stuck.append(f"{nid}: checks not passed ({summary.get('score')}/{summary.get('total')})")
    state = await lp.progress(db, user.id, language)
    incomplete = [n['id'] for n in state['nodes'] if not n['complete']]
    if incomplete:
        stuck.append(f'curriculum incomplete at: {incomplete[:5]}')
    if state['current_id'] is not None:
        stuck.append(f"learner is still routed to {state['current_id']} after finishing everything")
    return stuck


@pytest.mark.parametrize('language', sorted(lp.LANGUAGE_LABELS))
async def test_learner_can_finish_every_path_without_hitting_a_wall(db, language, monkeypatch):
    if not runnable_here(language) and any(i['language'] == language and i['type'] in quiz.CODE_TYPES for i in quiz.items(language).values()):
        pytest.skip(f'{language} code checks need its runner; run with EXEC_BACKEND=docker')
    from app.core.config import settings
    monkeypatch.setattr(quiz, 'judge_provider', lambda: None)
    # Hourly caps are abuse limits, tested separately; here they must not stop a full path.
    monkeypatch.setattr(settings, 'quiz_answers_per_hour', 100000)
    monkeypatch.setattr(settings, 'quiz_code_runs_per_hour', 100000)
    stuck = await walk(db, language)
    assert stuck == [], f'{language}: ' + '; '.join(stuck[:10])


def test_hourly_caps_let_one_sitting_finish_the_largest_path():
    from app.core.config import settings
    largest_checks = max(sum(len(quiz.pool(l, n['id'])) for n in lp.nodes(l)) for l in lp.LANGUAGE_LABELS)
    largest_code = max(sum(1 for n in lp.nodes(l) for i in quiz.pool(l, n['id']) if i['type'] in quiz.CODE_TYPES)
                       for l in lp.LANGUAGE_LABELS)
    assert settings.quiz_answers_per_hour >= largest_checks
    assert settings.quiz_code_runs_per_hour >= largest_code
