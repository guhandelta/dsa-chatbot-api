"""Authored Explain tiers. JavaScript is the pilot; no automatic language translation."""
from functools import lru_cache
import json
from pathlib import Path

from fastapi import HTTPException

from app.services import content_catalog, learning_path

PATH = Path(__file__).resolve().parents[2] / 'data/explain/javascript.json'


@lru_cache(maxsize=2)
def _load(version):
    return json.loads(PATH.read_text())


def authored():
    return _load(PATH.stat().st_mtime_ns)


def find_unit(language, unit_id):
    if not unit_id.startswith(f'explain:{language}:'):
        raise HTTPException(403, 'This Explain topic belongs to a different language.')
    if language != 'javascript':
        raise HTTPException(404, 'The tiered Explain pathway has not been reviewed for this language yet.')
    unit = next((u for u in authored()['units'] if u['id'] == unit_id), None)
    if unit is None:
        raise HTTPException(404, 'That Explain topic is not available.')
    return unit


def resolve_unit_focus(language, focus_id):
    unit_id, separator, activity_id = focus_id.partition('/')
    unit = find_unit(language, unit_id)
    activity = None
    if separator:
        activity = next((a for a in unit.get('activities', []) if a['id'] == activity_id), None)
        if activity is None:
            raise HTTPException(404, 'That activity does not belong to this Explain topic.')
    return unit, activity


def context(language, unit_id, activity_id=None):
    unit, activity = resolve_unit_focus(language, unit_id + ('/' + activity_id if activity_id else ''))
    selected = ''
    if activity:
        selected = (f"\n## Selected activity: {activity['title']}\n"
                    f"Route: {activity['route']}. Form: {activity['kind']}.\n"
                    f"{activity['prompt']}\nEvidence to discuss: {' '.join(activity['checklist'])}\n"
                    'Work on this selected activity, not another exercise from the unit. '
                    'Ask for a trace, explanation, tests or an attempt; do not give the complete implementation. '
                    'For review activities, describe this as deliberate review, not new mastery evidence.\n')
    return (f"# {unit['title']} — Tier {unit['tier']}\n"
            f"Objective: {unit['objective']}\nMental model: {unit['mental_model']}\n\n"
            f"## Structure and operations\n```{language}\n{unit['structure']['code']}\n```\n"
            f"Worked-example output: {unit['structure']['expected_output']}\n\n"
            f"## Applied problem (ungraded)\n{unit['applied_task']}\n\n"
            f"Pitfall: {unit['pitfall']}\n\n## DSA connection\n{unit['dsa_bridge']}\n{selected}"
            "Teach one step at a time. Ask the learner to trace and reason before progressing. "
            "Do not solve the applied task or linked DSA problems for them. "
            "This lesson and reflection are not assessment evidence.")


async def pathway(session, user_id, language):
    if language != 'javascript':
        return {'language': language, 'status': 'awaiting-language-review', 'tiers': [], 'units': [], 'foundations': []}
    data = authored()
    state = await learning_path.progress(session, user_id, language)
    nodes = {n['id']: n for n in state['nodes']}
    solved = await learning_path.passed_exercises(session, user_id, language)
    problems = {p.id: p for p in content_catalog.filter_content(track='dsa', language=language) if p.track == 'dsa'}
    units = []
    for unit in data['units']:
        node = nodes.get(unit['assessment_node_id'])
        units.append({**unit, 'assessment': None if node is None else {
            'node_id': node['id'], 'title': node['title'], 'checks_available': node['checks_available'],
            'checks_passed': node['checks_passed'], 'exercise_id': node['exercise_id'],
            'exercise_passed': node['exercise_passed'], 'coverage_ready': node['coverage_ready'],
        }, 'practice': [{'id': pid, 'title': problems[pid].title, 'difficulty': problems[pid].difficulty,
                         'solved': pid in solved} for pid in unit['practice_ids'] if pid in problems]})
    return {'language': language, 'status': data['status'], 'version': data['version'],
            'tiers': data['tiers'], 'units': units, 'authoring_profile': data.get('authoring_profile'),
            'foundations': [{'id': n['id'], 'title': n['title'], 'complete': n['complete']}
                            for n in state['nodes'] if n['kind'] == 'stage' and n['stage'] <= 4],
            'assessment_note': 'Lessons and applied prompts are ungraded. Linked checks and exercises '
                               'provide evidence for their own topics only; they do not certify an entire tier.'}
