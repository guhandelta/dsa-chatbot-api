"""Offline metadata and syntax ownership audit for the authored Explain pilot."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import content_catalog, explain_pathway, learning_path
from tools.audit_language_integrity import MARKERS


def audit():
    data = explain_pathway.authored()
    nodes = {n['id'] for n in learning_path.nodes('javascript')}
    problems = {p.id: p for p in content_catalog.filter_content(track='dsa') if p.track == 'dsa'}
    seen, errors, activity_ids = set(), [], set()
    activity_counts = Counter()
    for unit in data['units']:
        if not unit['id'].startswith('explain:javascript:') or unit['id'] in seen:
            errors.append(f"Invalid or duplicate unit ID: {unit['id']}")
        if not set(unit['prerequisite_ids']) <= seen:
            errors.append(f"Missing, out-of-order or cyclic prerequisite: {unit['id']}")
        seen.add(unit['id'])
        if unit['assessment_node_id'] and unit['assessment_node_id'] not in nodes:
            errors.append(f"Foreign or missing assessment: {unit['id']}")
        for pid in unit['practice_ids']:
            if pid not in problems or problems[pid].difficulty not in ('Easy', 'Medium'):
                errors.append(f"Missing or out-of-range DSA practice: {unit['id']}/{pid}")
        if not all(unit.get(key) for key in ('objective', 'mental_model', 'structure', 'applied_task', 'pitfall', 'dsa_bridge')):
            errors.append(f"Missing learning phase: {unit['id']}")
        activities = unit.get('activities', [])
        routes = Counter(a.get('route') for a in activities)
        if unit['tier'] == 1 and (len(activities) != 12 or routes != {'core': 8, 'extension': 3, 'review': 1}):
            errors.append(f"Incomplete basic practice ladder: {unit['id']}")
        prompts = set()
        for activity in activities:
            focus = unit['id'] + '/' + activity['id']
            if activity['id'] in activity_ids or len(focus) > 120 or '/' in activity['id']:
                errors.append(f"Duplicate or invalid activity focus: {focus}")
            activity_ids.add(activity['id'])
            if activity.get('assessment') != 'ungraded' or activity.get('source') != 'authored':
                errors.append(f"Unexpected assessment or source claim: {focus}")
            if not all(activity.get(k) for k in ('family_id', 'title', 'prompt', 'step', 'kind', 'route', 'checklist')):
                errors.append(f"Incomplete activity: {focus}")
            if activity['prompt'] in prompts:
                errors.append(f"Repeated prompt within a unit: {focus}")
            prompts.add(activity['prompt'])
            if activity.get('route') not in ('core', 'extension', 'review'):
                errors.append(f"Invalid activity route: {focus}")
            activity_counts[unit['tier']] += 1
        for language, marker in MARKERS.items():
            if language != 'javascript' and re.search(marker, unit['structure']['code']):
                errors.append(f"Foreign syntax: {language} in {unit['id']}")
    return {'status': 'fail' if errors else 'pass', 'language': 'javascript',
            'units': len(data['units']), 'per_tier': dict(Counter(u['tier'] for u in data['units'])),
            'activities': len(activity_ids), 'activities_per_tier': dict(activity_counts),
            'errors': errors,
            'limits': 'Static ownership, prerequisites and links. Authored example execution is tested separately; applied tasks are ungraded.'}


if __name__ == '__main__':
    result = audit()
    rendered = json.dumps(result, indent=2) + '\n'
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(rendered)
    print(rendered)
    raise SystemExit(bool(result['errors']))
