"""Count the data-quality problems from the 2026-10-18 knowledge base audit.

Run from API root: python3 -m tools.audit_reference_quality [records.jsonl] [--json out.json]
Read-only. Counts are over learner-retrievable rows (eligible()) unless noted.
"""
import argparse
from collections import Counter, defaultdict
import json
import re
from pathlib import Path
import sys

API = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API))

from app.services.knowledge_hygiene import (_near_duplicate_key, _payload_metadata, WATCH_OUT_DOCS)

LEGACY_PREFIX = 'Imported reference; not locally executed.'
RUBRIC = re.compile(r'RAG grader|grader should|\bred flag\b|good explanation|\brubric\b', re.I)
DATASET = re.compile(r'Training Data for the DSA Mentor|\bJSONL\b|chunk schema|\bRAG\b', re.I)


def first_content_line(row):
    lines = [l for l in row['document'].split('\n') if l.strip()]
    if not lines:
        return ''
    if lines[0].startswith(LEGACY_PREFIX) or lines[0].startswith('Context: '):
        lines = lines[1:]
    payload = row.get('payload')
    if isinstance(payload, dict) and payload.get('chunking') == 'heading-sections-v1':
        lines = lines[1:]  # title line
    return lines[0].strip() if lines else ''


def report(rows):
    from app.services.reference_library import eligible
    public = [r for r in rows if eligible(r)]
    out = {'records': len(rows), 'public': len(public),
           'public_by_subject': dict(sorted(Counter(r['metadata']['subject'] for r in public).items())),
           'duplicate_ids': sum(n - 1 for n in Counter(r['id'] for r in rows).values() if n > 1),
           'public_with_answer_flag_not_false': sum(r['metadata'].get('contains_answer') is not False for r in public),
           'public_claiming_verified': sum(bool(r['metadata'].get('verified')) for r in public)}
    out['legacy_prefix'] = sum(r['document'].startswith(LEGACY_PREFIX) for r in public)
    out['trailing_chunk_id'] = sum(bool(re.search(r'\nChunk: \S+\s*$', r['document'])) for r in public)
    # Framework section rows start "<subject> reference — <title>" by design.
    mid = [r for r in public if isinstance(r.get('payload'), dict) and 'source_sha256' in r['payload']
           and not re.match(r'[a-z-]+ reference — ', r['document'])
           and re.match(r'[a-z,;.)\]}]', first_content_line(r))]
    out['starts_mid_sentence'] = len(mid)
    out['starts_mid_sentence_by_subject'] = dict(Counter(r['metadata']['subject'] for r in mid))
    rubric = [r for r in public if RUBRIC.search(r['document'])]
    out['rubric_language'] = len(rubric)
    out['rubric_language_by_subject'] = dict(Counter(r['metadata']['subject'] for r in rubric))
    out['dataset_talk'] = sum(bool(DATASET.search(r['document'])) for r in public)
    exact, near = defaultdict(list), defaultdict(list)
    for r in public:
        m = r['metadata']
        exact[(m['subject'], re.sub(r'\s+', ' ', r['document']).strip())].append(r['id'])
        near[(m['subject'], _near_duplicate_key(r))].append(r['id'])
    out['exact_duplicate_rows_within_subject'] = sum(len(v) - 1 for v in exact.values() if len(v) > 1)
    out['near_duplicate_rows_within_subject'] = sum(len(v) - 1 for v in near.values() if len(v) > 1)
    frameworks = defaultdict(set)
    for r in public:
        if r['metadata']['subject'] in ('python-django', 'python-fastapi', 'python-flask'):
            frameworks[_near_duplicate_key(r)].add(r['metadata']['subject'])
    out['framework_text_shared_across_subjects'] = sum(len(s) > 1 for s in frameworks.values())
    out['embedded_rows_under_plain_c'] = sum(
        r['metadata']['subject'] == 'c' and (_payload_metadata(r).get('track') == 'embedded_c'
                                             or str(_payload_metadata(r).get('doc', '')).startswith('ec_')) for r in rows)
    out['strategy_rows_with_why_label_in_watch_out_docs'] = sum(
        str(_payload_metadata(r).get('doc', '')).startswith(WATCH_OUT_DOCS) and bool(re.search(r'^Why: ', r['document'], re.M))
        for r in public)
    out['public_with_level'] = sum('level' in r['metadata'] for r in public)
    out['level_values'] = dict(Counter(r['metadata']['level'] for r in public if 'level' in r['metadata']))
    out['public_with_data_structure_id'] = sum('data_structure_id' in r['metadata'] for r in public)
    out['distinct_data_structure_ids'] = len({r['metadata']['data_structure_id'] for r in public if 'data_structure_id' in r['metadata']})
    out['public_under_150_chars'] = sum(len(r['document']) < 150 for r in public)
    out['public_empty'] = sum(not r['document'].strip() for r in public)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', nargs='?', type=Path, default=API / 'data/reference_library/records.jsonl')
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.records.open(encoding='utf-8') if line.strip()]
    result = report(rows)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
