"""Answer-free debugging missions, with durable per-learner no-repeat history.

Cases are authored repairs, output investigations, or reviewed bad/good pairs.
Only the code under investigation and an answer-free brief are shown. No model generation or code execution happens
when drawing/reviewing a mission; self-review never grants mastery or rewards.
"""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random
import re

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.db.models import DebugChallengeAttempt
from app.services import reference_library

DIFFICULTIES = ('easy', 'medium', 'hard', 'expert', 'extreme')
BANK_PATH = Path(__file__).resolve().parents[2] / 'data/debug/knowledge-base.json'
LEVEL_DIFFICULTY = {'L0': 'easy', 'L1': 'easy', 'L2': 'medium', 'L3': 'hard', 'L4': 'expert', 'L5': 'extreme', 'L6': 'extreme'}


def _fingerprint(language, subject, code):
    # Formatting-only edits and duplicated imports from different sources cannot
    # produce a new problem. Keep operators/literals so distinct bugs stay distinct.
    normalized = re.sub(r'\s+', '', code)
    return 'debug-' + hashlib.sha256(f'{language}\0{subject}\0{normalized}'.encode()).hexdigest()[:48]


def bank():
    return _bank(BANK_PATH.stat().st_mtime_ns)


def quiz_languages():
    from app.services.learning_path import LANGUAGE_LABELS
    return tuple(LANGUAGE_LABELS)


@lru_cache(maxsize=2)
def _bank(version):
    # Runtime reads only the dedicated bank. Editing quizzes/reference lessons
    # cannot silently publish new debugging problems or change assigned cases.
    items = json.loads(BANK_PATH.read_text())['items']
    return {item['id']: item for item in items}


PUBLIC_FIELDS = ('id', 'language', 'subject', 'difficulty', 'title', 'code', 'failure', 'goal', 'source', 'code_language', 'task_kind')


def public(item, attempt=None):
    from app.services.understanding import prompts
    assessment = json.loads(attempt.understanding_json)['assessment'] if attempt and attempt.understanding_json else None
    return {**{k: item[k] for k in PUBLIC_FIELDS},
            'attempt_id': attempt.id if attempt else None,
            'status': attempt.status if attempt else None,
            'assessment': 'rubric-model' if assessment else 'understanding-check',
            'automatically_graded': bool(assessment), 'code_executed': False,
            'understanding': prompts('debug'),
            'understanding_result': assessment}


async def assess_diagnosis(session, user, attempt_id, diagnosis, reasoning, transfer):
    from app.services import quiz, understanding
    row = await session.get(DebugChallengeAttempt, attempt_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, 'Debugging challenge not found.')
    from app.services.language_access import require_language
    await require_language(session, user, row.language)
    if row.status != 'assigned':
        raise HTTPException(409, 'Choose an active debugging challenge before submitting.')
    understanding.validate(reasoning, transfer)
    if not diagnosis.strip() or len(diagnosis) > 4000:
        raise HTTPException(422, 'Include a diagnosis up to 4000 characters.')
    if row.reviewed_at:
        last = row.reviewed_at.replace(tzinfo=timezone.utc) if row.reviewed_at.tzinfo is None else row.reviewed_at
        if (datetime.now(timezone.utc) - last).total_seconds() < 60:
            raise HTTPException(429, 'Take a moment to revise your reasoning before checking again.')
    item = bank().get(row.challenge_id)
    if not item:
        raise HTTPException(410, 'This debugging challenge was retired. Choose a new one.')
    await quiz.enforce_budget(session, user.id, 'explain')
    provider = quiz.judge_provider()
    if not provider:
        raise HTTPException(503, 'The understanding grader is unavailable. Keep your diagnosis and retry later.')
    # Reserve the attempt before contacting the model: parallel clicks cannot
    # buy multiple evaluations, and stale replies cannot review a skipped case.
    reserved_at = datetime.now(timezone.utc)
    reserved = await session.execute(update(DebugChallengeAttempt).where(
        DebugChallengeAttempt.id == row.id, DebugChallengeAttempt.status == 'assigned',
        DebugChallengeAttempt.reviewed_at == row.reviewed_at,
    ).values(reviewed_at=reserved_at).execution_options(synchronize_session=False))
    if reserved.rowcount != 1:
        raise HTTPException(409, 'This diagnosis is already being checked. Reload before retrying.')
    await understanding.reserve_usage(session, user.id)
    await session.commit()
    result = await understanding.assess(language=row.language,
        question='\n'.join([item['title'], item['code'], item['failure'], item['goal']]),
        reference=item['solution'], response=diagnosis, reasoning=reasoning, transfer=transfer,
        kind='debug', provider=provider)
    # Diagnosis correctness is part of the reasoning rubric, not inferred from style.
    status = 'reviewed' if result['passed'] else 'assigned'
    saved = await session.execute(update(DebugChallengeAttempt).where(
        DebugChallengeAttempt.id == row.id, DebugChallengeAttempt.status == 'assigned',
        DebugChallengeAttempt.reviewed_at == reserved_at,
    ).values(diagnosis=diagnosis.strip(),
        understanding_json=json.dumps(dict(reasoning=reasoning, transfer=transfer, assessment=result)),
        reviewed_at=datetime.now(timezone.utc), status=status).execution_options(synchronize_session=False))
    if saved.rowcount != 1:
        await session.rollback()
        raise HTTPException(409, 'The active challenge changed while checking. Reload to continue.')
    await session.commit()
    await session.refresh(row)
    return {'attempt_id': row.id, 'status': status, 'understanding': result,
            'assessment': 'rubric-model', 'code_executed': False}


def _mapped_nodes(language, topic, meta, payload):
    from app.services.learning_path import SPINE, stage_node_id
    keys = {str(v).lower() for v in (meta.get('data_structure_id'), meta.get('data_structure'), payload.get('data_structure')) if v}
    # Use declared curriculum categories. Incidental words such as "this" or
    # "error" must not assign arbitrary examples to language depth modules.
    return [stage_node_id(language, stage) for stage in SPINE if keys & set(stage.data_structures)]


def selected_scope(language, focus_id=None):
    if not focus_id:
        return None
    if focus_id.startswith('explain:'):
        from app.services.explain_pathway import resolve_unit_focus
        unit, _ = resolve_unit_focus(language, focus_id)
        # Basic topics reuse their exact assessed topic. Combined topics need
        # dedicated tags; do not substitute a loosely related foundation case.
        if unit['assessment_node_id']:
            return {'id': unit['assessment_node_id'], 'title': unit['title'], 'kind': 'node'}
        return {'id': unit['id'], 'title': unit['title'], 'kind': 'explain-unit'}
    from app.services.learning_path import find_node, node_for_exercise, stage_node_id
    node = find_node(language, focus_id)
    if node:
        return {'id': node['id'], 'title': node['title'], 'kind': 'node'}
    exercise = node_for_exercise(focus_id)
    if exercise:
        if exercise[0] != language:
            raise HTTPException(403, 'Choose the current topic language before debugging it.')
        return {'id': stage_node_id(language, exercise[1]), 'title': exercise[1].title, 'kind': 'node'}
    if focus_id.startswith('subject:'):
        subject = focus_id.removeprefix('subject:')
        found = next((s for s in reference_library.subjects() if s['id'] == subject), None)
        if not found or found['language'] != language:
            raise HTTPException(403, 'This reference subject does not belong to the selected language.')
        return {'id': focus_id, 'title': subject.replace('-', ' '), 'kind': 'subject', 'subject': subject}
    raise HTTPException(404, 'That topic is not part of the selected language path.')


def in_scope(item, scope):
    if scope is None:
        return True
    if scope['kind'] == 'explain-unit':
        return scope['id'] in item.get('explain_unit_ids', [])
    if scope['kind'] == 'subject':
        return item['subject'] == scope['subject']
    # A core path topic must never silently widen to a framework or another node.
    return item['subject'] == item['language'] and scope['id'] in item['node_ids']


def pool(language, subject, difficulty, focus_id=None):
    if difficulty not in DIFFICULTIES:
        raise HTTPException(422, 'Choose a supported debugging difficulty.')
    subjects = {i['subject'] for i in bank().values() if i['language'] == language}
    if subject not in subjects:
        raise HTTPException(422, 'Choose a debugging subject belonging to the selected language.')
    scope = selected_scope(language, focus_id)
    return [i for i in bank().values() if (i['language'], i['subject'], i['difficulty']) == (language, subject, difficulty) and in_scope(i, scope)]


async def catalog(session, user, language, focus_id=None):
    scope = selected_scope(language, focus_id)
    items = [i for i in bank().values() if i['language'] == language and in_scope(i, scope)]
    all_items = {i['id']: i for i in items}
    attempts = (await session.scalars(select(DebugChallengeAttempt).where(
        DebugChallengeAttempt.user_id == user.id, DebugChallengeAttempt.language == language))).all()
    seen = {a.challenge_id for a in attempts}
    current = {}
    for attempt in sorted(attempts, key=lambda a: a.created_at):
        if attempt.status == 'assigned' and attempt.challenge_id in all_items:
            current[(attempt.subject, attempt.difficulty)] = public(all_items[attempt.challenge_id], attempt)
    totals = Counter((i['subject'], i['difficulty']) for i in items)
    unseen = Counter((i['subject'], i['difficulty']) for i in items if i['id'] not in seen)
    reviewed = Counter((a.subject, a.difficulty) for a in attempts if a.status == 'reviewed' and a.challenge_id in all_items)
    return {'language': language, 'scope': scope, 'difficulties': list(DIFFICULTIES), 'subjects': [
        {'id': subject, 'levels': [dict(difficulty=d, total=totals[subject, d],
                                      remaining=unseen[subject, d], reviewed=reviewed[subject, d],
                                      current=current.get((subject, d))) for d in DIFFICULTIES]}
        for subject in sorted({i['subject'] for i in items}, key=lambda s: (s != language, s))]}


async def next_challenge(session, user, language, subject, difficulty, focus_id=None):
    candidates = pool(language, subject, difficulty, focus_id)
    seen = set((await session.scalars(select(DebugChallengeAttempt.challenge_id).where(
        DebugChallengeAttempt.user_id == user.id))).all())
    # Shuffle only unseen problems. The database's unique constraint, rather than
    # browser storage or random choice, enforces the no-repeat rule.
    random.SystemRandom().shuffle(candidates)
    for item in candidates:
        if item['id'] in seen:
            continue
        row = DebugChallengeAttempt(user_id=user.id, challenge_id=item['id'], language=language,
                                    subject=subject, difficulty=difficulty)
        try:
            async with session.begin_nested():
                session.add(row)
                await session.flush()
                await session.execute(update(DebugChallengeAttempt).where(
                    DebugChallengeAttempt.user_id == user.id,
                    DebugChallengeAttempt.language == language,
                    DebugChallengeAttempt.subject == subject,
                    DebugChallengeAttempt.difficulty == difficulty,
                    DebugChallengeAttempt.status == 'assigned',
                    DebugChallengeAttempt.id != row.id,
                    *([DebugChallengeAttempt.challenge_id.in_([i['id'] for i in candidates])] if focus_id else []),
                ).values(status='skipped'))
        except IntegrityError:
            continue  # Another request reserved this problem first.
        await session.commit()
        return public(item, row)
    raise HTTPException(409, 'No unseen problems remain for this topic at this level. Choose another difficulty; unrelated topics are never substituted.')


async def review(session, user, attempt_id, diagnosis):
    diagnosis = diagnosis.strip()
    if len(diagnosis) < 10:
        raise HTTPException(422, 'Describe the diagnosis and a regression test in at least ten characters.')
    row = await session.get(DebugChallengeAttempt, attempt_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, 'Debugging challenge not found.')
    from app.services.language_access import require_language
    await require_language(session, user, row.language)
    if row.understanding_json:
        raise HTTPException(409, 'Use the understanding check to revise this assessed diagnosis.')
    row.status = 'reviewed'
    row.diagnosis = diagnosis
    row.reviewed_at = datetime.now(timezone.utc)
    await session.commit()
    return {'attempt_id': row.id, 'status': row.status, 'automatically_graded': False}


async def focus(session, user_id, language, attempt_id):
    row = await session.get(DebugChallengeAttempt, attempt_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(404, 'Debugging challenge not found.')
    if row.language != language:
        raise HTTPException(403, 'Choose the debugging challenge language before opening it.')
    item = bank().get(row.challenge_id)
    if item is None:
        raise HTTPException(409, 'This debugging challenge was retired. Choose a new problem.')
    return {'kind': 'language', 'id': 'debug:' + row.id,
            'title': f"{row.subject}: {item['title']} ({row.difficulty})",
            'auto': False, 'goal': item['goal']}
