"""Offline coverage and answer-safety audit for the complete debug bank."""
from collections import Counter
import json
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services import debug_challenges as dc, reference_library, learning_path as lp
from tools.audit_language_integrity import MARKERS


def audit():
    items = dc.bank()
    ownership = {s['id']: s['language'] for s in reference_library.subjects()}
    counts = Counter((i['subject'], i['difficulty']) for i in items.values())
    errors, seen = [], set()
    for item in items.values():
        key = dc._fingerprint(item['language'], item['subject'], item['code'])
        if key in seen or key != item['id']:
            errors.append(f"Duplicate or unstable fingerprint: {item['id']}")
        seen.add(key)
        from app.services.explain_pathway import find_unit
        for unit_id in item.get('explain_unit_ids', []):
            try:
                find_unit(item['language'], unit_id)
            except Exception:
                errors.append(f"Invalid Explain topic assignment: {item['id']}/{unit_id}")
        expected_language = item['code_language']
        for detected, pattern in MARKERS.items():
            if detected == expected_language or (expected_language, detected) in (('typescript','javascript'),('cpp','c')):
                continue
            if re.search(pattern, item['code']):
                errors.append(f"Foreign syntax in {item['id']}: {detected} in {expected_language}")
        if ownership.get(item['subject']) != item['language']:
            errors.append(f"Language/subject mismatch: {item['id']}")
        if not all(str(item.get(k, '')).strip() for k in ('code','failure','goal','solution')):
            errors.append(f"Missing problem/QA material: {item['id']}")
        if 'solution' in dc.public(item) or 'private_solution' in dc.public(item):
            errors.append(f"Answer exposed: {item['id']}")
    path_nodes = {n['id'] for language in lp.LANGUAGE_LABELS for n in lp.nodes(language)}
    node_counts = Counter(n for item in items.values() if item['subject'] == item['language'] for n in item['node_ids'])
    for node in path_nodes:
        if not node_counts[node]:
            errors.append(f'Missing topic-specific debugging content: {node}')
    for item in items.values():
        if any(n not in path_nodes or not n.startswith(item['language'] + ':') for n in item['node_ids']):
            errors.append(f'Invalid topic assignment: {item["id"]}')
    for subject in ownership:
        for difficulty in dc.DIFFICULTIES:
            if counts[subject, difficulty] < 2:
                errors.append(f"Need at least two distinct problems: {subject}/{difficulty}")
    return dict(status='pass' if not errors else 'fail', total=len(items),
                authored=Counter(i['source'] for i in items.values()),
                languages=len({i['language'] for i in items.values()}), subjects=len(ownership),
                scoped_path_topics=len(path_nodes), per_topic=dict(sorted(node_counts.items())),
                per_subject={s:{d:counts[s,d] for d in dc.DIFFICULTIES} for s in sorted(ownership)},
                assessment='self-review; not automatic execution/grading', errors=errors)


if __name__ == '__main__':
    result = audit()
    text = json.dumps(result, indent=2) + '\n'
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text)
    print(text)
    raise SystemExit(bool(result['errors']))
