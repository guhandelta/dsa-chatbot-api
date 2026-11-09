"""Free, deterministic progress summaries with explicit evidence and denominators."""
from collections import Counter

from sqlalchemy import func, select

from app.db.models import DebugChallengeAttempt, LearningEvent, StudentPathRecord
from app.services import content_catalog, debug_challenges, learning_path


async def overview(session, user_id, language):
    path = await learning_path.progress(session, user_id, language)
    problems = {c.id for c in content_catalog.filter_content(language=language) if c.track == 'dsa'}
    events = (await session.execute(select(LearningEvent.problem_id, LearningEvent.kind).where(
        LearningEvent.user_id == user_id, LearningEvent.language == language,
        LearningEvent.problem_id.in_(problems),
        LearningEvent.kind.in_(('solved', 'attempt', 'evaluated'))))).all()
    solved = {pid for pid, kind in events if kind == 'solved'}
    started = {pid for pid, _ in events} - solved
    cases = {i['id'] for i in debug_challenges.bank().values() if i['language'] == language}
    attempts = (await session.execute(select(DebugChallengeAttempt.challenge_id, DebugChallengeAttempt.status).where(
        DebugChallengeAttempt.user_id == user_id, DebugChallengeAttempt.language == language))).all()
    # Retired cases remain in history, but cannot inflate current-bank coverage.
    statuses = Counter(status for cid, status in attempts if cid in cases)
    lessons = content_catalog.filter_content(track='design-patterns', language=language)
    return {'language': language, 'sections': [
        {'id': 'learning-path', 'title': 'Learning Path', 'metric': 'Current path checkpoints',
         'completed': path['completed'], 'total': path['total'],
         'in_progress': sum(n['status'] == 'in-progress' for n in path['nodes']),
         'status': 'available' if path['coverage_ready'] else 'content-incomplete',
         'detail': path['mastery_rule']},
        {'id': 'dsa', 'title': 'DSA Practice', 'metric': 'Problems solved',
         'completed': len(solved), 'total': len(problems), 'in_progress': len(started),
         'status': 'available' if problems else 'coming-soon',
         'detail': 'Unique problems with recorded passing evaluations in this language. Repeat solves count once.'},
        {'id': 'debug', 'title': 'Debug with Me', 'metric': 'Self-reviewed cases',
         'completed': statuses['reviewed'], 'total': len(cases),
         'in_progress': statuses['assigned'] + statuses['skipped'],
         'status': 'available' if cases else 'coming-soon',
         'detail': 'Activity across this language and its frameworks. Opened or skipped cases remain unfinished. Self-review is not assessed mastery.'},
        {'id': 'design-patterns', 'title': 'Design Patterns', 'metric': 'Assessment coming soon',
         'completed': None, 'total': None, 'in_progress': 0,
         'status': 'coming-soon', 'lessons_available': len(lessons),
         'detail': f'{len(lessons)} reference lessons available. A graded pathway and mastery tracking are coming soon.'},
    ]}


async def profile_overview(session, user_id, languages):
    """One profile view; preserve distinct evidence labels across sections."""
    rows = (await session.execute(select(StudentPathRecord.section, StudentPathRecord.kind, func.count())
                                  .where(StudentPathRecord.user_id == user_id)
                                  .group_by(StudentPathRecord.section, StudentPathRecord.kind))).all()
    records = {section: {kind: count for row_section, kind, count in rows if row_section == section}
               for section in ('language', 'dsa', 'design-patterns')}
    per_language = []
    for language in languages:
        result = await overview(session, user_id, language)
        per_language.append({'language': language,
                             'sections': [item for item in result['sections']
                                          if item['id'] in ('learning-path', 'dsa', 'design-patterns')]})
    return {'languages': per_language, 'student_records': records,
            'summary_rule': 'Section measures are separate; problem solves and reference readings are not mastery.'}
