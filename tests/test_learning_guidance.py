from datetime import datetime, timedelta, timezone

from app.db.models import LearningEvent, QuizAnswer, QuizSession
from app.services.learning_guidance import guidance
from tests.test_study_room import register


async def answers(db, uid, language, node, responses, offset=0, completed=True):
    now = datetime.now(timezone.utc) + timedelta(seconds=offset)
    quiz = QuizSession(user_id=uid, language=language, node_id=node,
                       completed_at=now if completed else None, total=len(responses))
    db.add(quiz)
    await db.flush()
    for index, (item, concept, correct) in enumerate(responses):
        db.add(QuizAnswer(quiz_id=quiz.id, user_id=uid, item_id=item, concept=concept,
            item_type='mcq', correct=correct, score=int(correct), created_at=now + timedelta(microseconds=index)))
    await db.commit()


async def test_tips_distinguish_misses_strengths_and_related_extension(client, db):
    headers, uid = await register(client, db, 'tips@example.com', ('javascript',))
    await answers(db, uid, 'javascript', 'javascript:stage-06',
                  [('a1', 'array-copy', True), ('a2', 'array-copy', True), ('b1', 'array-index', False)])
    await answers(db, uid, 'javascript', 'javascript:stage-06', [('a3', 'array-copy', True)], 1)
    response = await client.get('/study/insights', headers=headers, params={'language': 'javascript'})
    tips = response.json()['guidance']
    assert tips['focus'][0]['title'] == 'Hone array index'
    assert '1 of 1' in tips['focus'][0]['evidence']
    assert tips['strengths'][0]['title'] == 'Build on array copy'
    assert '3 of 3' in tips['strengths'][0]['evidence']
    assert tips['strengths'][0]['action']['focus'] == 'explain:javascript:arrays-strings'


async def test_repeating_one_question_does_not_create_a_strength(client, db):
    _, uid = await register(client, db, 'repeat-tips@example.com', ('javascript',))
    for offset in range(4):
        await answers(db, uid, 'javascript', 'javascript:stage-06', [('one-item', 'array-copy', True)], offset)
    tips = await guidance(db, uid, 'javascript')
    assert tips['strengths'] == []


async def test_latest_answer_wins_and_unfinished_other_user_language_data_is_excluded(client, db):
    _, uid = await register(client, db, 'isolated-tips@example.com', ('javascript', 'python'))
    _, other = await register(client, db, 'other-tips@example.com', ('javascript',))
    await answers(db, uid, 'javascript', 'javascript:stage-06',
                  [('one', 'copy', True), ('two', 'copy', True)], 0)
    await answers(db, uid, 'javascript', 'javascript:stage-06', [('three', 'copy', True)], 1)
    await answers(db, uid, 'javascript', 'javascript:stage-06', [('one', 'copy', False)], 2)
    await answers(db, uid, 'javascript', 'javascript:stage-06', [('four', 'copy', True)], 3, completed=False)
    await answers(db, uid, 'python', 'python:stage-06', [('foreign', 'python-only', False)], 4)
    await answers(db, other, 'javascript', 'javascript:stage-06', [('other', 'other-user', False)], 5)
    tips = await guidance(db, uid, 'javascript')
    assert tips['strengths'] == []
    assert len(tips['focus']) == 1 and tips['focus'][0]['title'] == 'Hone copy'
    assert '1 of 3' in tips['focus'][0]['evidence']


async def test_dsa_tips_use_unique_passing_problems_in_selected_language(client, db):
    _, uid = await register(client, db, 'dsa-tips@example.com', ('javascript', 'python'))
    for pid in ('two-sum', 'two-sum', 'contains-duplicate', 'product-of-array-except-self'):
        db.add(LearningEvent(user_id=uid, language='javascript', problem_id=pid, kind='solved'))
    for _ in range(2):
        db.add(LearningEvent(user_id=uid, language='javascript', problem_id='best-time-to-buy-and-sell-stock', kind='attempt'))
    db.add(LearningEvent(user_id=uid, language='python', problem_id='best-time-to-buy-and-sell-stock', kind='solved'))
    await db.commit()
    tips = await guidance(db, uid, 'javascript')
    assert tips['strengths'][0]['title'] == 'Build on DSA: arrays'
    assert '3 distinct' in tips['strengths'][0]['evidence']
    assert any(t['title'].startswith('Revisit Largest Gain from One Trade') for t in tips['focus'])
