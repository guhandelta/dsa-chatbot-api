"""Evidence-based skill tips. No model calls, personality inference, or quiz-repeat inflation."""
from collections import Counter, defaultdict

from sqlalchemy import select

from app.db.models import LearningEvent, QuizAnswer, QuizSession
from app.services import content_catalog, learning_path


async def guidance(session, user_id, language):
    state = await learning_path.progress(session, user_id, language)
    nodes = {n['id']: n for n in state['nodes']}
    rows = (await session.execute(select(QuizAnswer, QuizSession.node_id).join(
        QuizSession, QuizSession.id == QuizAnswer.quiz_id).where(
        QuizAnswer.user_id == user_id, QuizSession.user_id == user_id,
        QuizSession.language == language, QuizSession.completed_at.is_not(None)
    ).order_by(QuizAnswer.created_at.desc(), QuizAnswer.id.desc()).limit(300))).all()
    latest = {}
    for answer, node_id in rows:
        latest.setdefault(answer.item_id, (answer, node_id))
    groups = defaultdict(list)
    for answer, node_id in latest.values():
        if answer.concept and node_id in nodes:
            groups[(answer.concept, node_id)].append(answer)
    signals = []
    for (concept, node_id), answers in groups.items():
        correct = sum(a.correct for a in answers)
        signals.append({'concept': concept, 'node_id': node_id, 'correct': correct,
                        'total': len(answers), 'misses': len(answers) - correct,
                        'sessions': len({a.quiz_id for a in answers})})
    focus, strengths = [], []
    for signal in sorted(signals, key=lambda x: (x['correct'] / x['total'], -x['misses'], x['concept'])):
        if not signal['misses']:
            continue
        node = nodes[signal['node_id']]
        focus.append({'title': f"Hone {signal['concept'].replace('-', ' ')}",
            'evidence': f"{signal['misses']} of {signal['total']} distinct recently answered questions missed in {node['title']}.",
            'tip': 'Trace a small example, explain the first unexpected step, then test an empty or boundary input before retaking the checks.',
            'action': {'label': 'Review this concept', 'mode': 'explain', 'focus': node['id']}})
        if len(focus) == 3:
            break
    for signal in sorted(signals, key=lambda x: (-x['correct'] / x['total'], -x['total'], x['concept'])):
        if signal['total'] < 3 or signal['sessions'] < 2 or signal['correct'] / signal['total'] < .8:
            continue
        node = nodes[signal['node_id']]
        action = {'label': 'Explain a new edge case', 'mode': 'explain', 'focus': node['id']}
        tip = 'Try a new edge case without notes, then explain why your approach works and what extra space it uses.'
        if language == 'javascript':
            from app.services.explain_pathway import authored
            basic = next((u for u in authored()['units'] if u['assessment_node_id'] == node['id']), None)
            extension = next((u for u in authored()['units'] if u['tier'] == 2 and basic
                              and basic['id'] in u['prerequisite_ids']), None)
            if extension:
                action = {'label': f"Explore {extension['title']}", 'mode': 'explain', 'focus': extension['id']}
                tip = 'Build on this result by combining structures. Check the listed prerequisites before attempting the applied task.'
        strengths.append({'title': f"Build on {signal['concept'].replace('-', ' ')}",
            'evidence': f"{signal['correct']} of {signal['total']} distinct recent answers correct across {signal['sessions']} completed quizzes in {node['title']}.",
            'tip': tip, 'action': action})
        if len(strengths) == 3:
            break
    problems = {p.id: p for p in content_catalog.filter_content(track='dsa', language=language) if p.track == 'dsa'}
    events = (await session.execute(select(LearningEvent.problem_id, LearningEvent.kind).where(
        LearningEvent.user_id == user_id, LearningEvent.language == language,
        LearningEvent.problem_id.in_(problems), LearningEvent.kind.in_(('solved', 'attempt'))))).all()
    solved = {pid for pid, kind in events if kind == 'solved'}
    attempts = Counter(pid for pid, kind in events if kind == 'attempt' and pid not in solved)
    stalled = next((pid for pid, count in attempts.most_common() if count >= 2), None)
    if stalled:
        related = next((n for n in state['nodes'] if any(p['id'] == stalled for p in n['practice'])), None)
        if related:
            focus = focus[:2] + [{'title': f"Revisit {problems[stalled].title}",
                'evidence': f"{attempts[stalled]} recorded attempts without a passing evaluation in this language.",
                'tip': 'Return to a small input, write the expected state at each step, and identify a boundary case before resubmitting.',
                'action': {'label': 'Review the related foundation', 'mode': 'explain', 'focus': related['id']}}]
    tags = defaultdict(set)
    for pid in solved:
        for tag in problems[pid].algorithms:
            tags[tag].add(pid)
    for tag, ids in sorted(tags.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        if len(ids) < 3:
            continue
        related = next((n for n in state['nodes'] if any(p['id'] in ids for p in n['practice'])), None)
        if related:
            strengths = strengths[:2] + [{'title': f"Build on DSA: {tag.replace('-', ' ')}",
                'evidence': f"{len(ids)} distinct catalog problems tagged {tag} have recorded passing evaluations in this language.",
                'tip': 'Try a fresh related problem without hints. Explain the invariant, time cost and extra space; recorded solves alone do not establish independent mastery.',
                'action': {'label': 'Explore related practice', 'mode': 'explain', 'focus': related['id']}}]
            break
    current = nodes.get(state['current_id'])
    if not focus:
        focus.append({'title': 'Establish your next baseline' if not signals else 'Check transfer to a fresh problem',
            'evidence': 'No recent missed-question signal is available.' if signals else 'No completed topic-check evidence yet.',
            'tip': 'Explain the current concept in your own words, try a boundary case, then take its checks.',
            'action': {'label': 'Study the current topic', 'mode': 'explain', 'focus': current['id']} if current else None})
    return {'focus': focus, 'strengths': strengths,
            'strengths_empty': 'Complete at least three different questions on a concept across two quizzes, '
                               'with at least 80% correct on their latest answers, or solve three related DSA problems.',
            'evidence_note': 'Uses the latest response per question from the most recent 300 answers in completed quizzes, '
                             'plus unique recorded DSA solves in this language. Repeating one question or solve does not add evidence. '
                             'These are study suggestions, not a certification of mastery.'}
