"""Validate a knowledge-gap dataset package without credentials or model calls."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

LANGUAGES = {'java', 'javascript', 'python', 'c', 'cpp', 'rust', 'ruby', 'typescript', 'go', 'csharp', 'html', 'css'}


def default_package():
    here = Path(__file__).resolve()
    local = here.parents[1]
    if (local / 'manifest.json').exists(): return local
    return here.parents[2] / 'Training Data/generated/knowledge-gap-fill-v1'


def load_rows(path):
    with path.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]


def validate(package):
    errors = []
    manifest = json.loads((package / 'manifest.json').read_text())
    path = package / 'all_records.jsonl'
    raw = path.read_bytes()
    rows = load_rows(path)
    if hashlib.sha256(raw).hexdigest() != manifest['all_records_sha256']: errors.append('Combined file hash mismatch')
    if len(rows) != manifest['record_count']: errors.append('Combined record count mismatch')
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)): errors.append('Duplicate record IDs')
    fingerprints = set()
    for row in rows:
        rid = row['id']
        metadata = row['metadata']
        for key in ('language', 'subject', 'kind', 'source', 'origin', 'baseline', 'review_status', 'doc_url'):
            if not metadata.get(key): errors.append(f'{rid}: missing {key}')
        if metadata['language'] not in LANGUAGES: errors.append(f'{rid}: invalid language')
        if any(not isinstance(v, (str, bool, int, float)) for v in metadata.values()): errors.append(f'{rid}: metadata must contain scalars')
        if metadata.get('contains_answer') is not False: errors.append(f'{rid}: private answer flag')
        if metadata.get('kind') not in ('concept', 'reference'): errors.append(f'{rid}: private/non-reference kind')
        if metadata.get('verified') is not False or metadata.get('executable') is not False:
            errors.append(f'{rid}: unsupported execution/certification flag')
        text = row['document']
        if len(text.split()) < 70: errors.append(f'{rid}: undersized reference')
        if re.search(r'\b(?:TODO|TBD|lorem ipsum)\b', text, re.I): errors.append(f'{rid}: placeholder')
        if text.count('```') % 2: errors.append(f'{rid}: unbalanced code fence')
        key = (metadata['language'], metadata['subject'], re.sub(r'\s+', ' ', text).strip())
        if key in fingerprints: errors.append(f'{rid}: duplicate scoped public text')
        fingerprints.add(key)
        if not row.get('provenance') or any(urlparse(u).scheme != 'https' or not urlparse(u).hostname for u in row['provenance']):
            errors.append(f'{rid}: invalid source URLs')
        payload = row.get('payload', {})
        if payload.get('content_sha256') and hashlib.sha256(text.encode()).hexdigest() != payload['content_sha256']:
            errors.append(f'{rid}: content hash mismatch')
    batch_ids = []
    for batch in manifest['batches']:
        batch_path = package / batch['path']
        if hashlib.sha256(batch_path.read_bytes()).hexdigest() != batch['sha256']: errors.append(f'{batch_path.name}: hash mismatch')
        batch_rows = load_rows(batch_path)
        if len(batch_rows) != batch['records']: errors.append(f'{batch_path.name}: count mismatch')
        if any(r['metadata']['subject'] != batch['subject'] for r in batch_rows): errors.append(f'{batch_path.name}: scope mismatch')
        batch_ids.extend(r['id'] for r in batch_rows)
    if Counter(batch_ids) != Counter(ids): errors.append('Batch exports do not match combined records')
    coverage = list(csv.DictReader((package / 'coverage.csv').open()))
    known_gaps = {r['gap_id'] for r in coverage}
    if any(r['status'] == 'unmapped' for r in coverage): errors.append('Unmapped gap section')
    for row in rows:
        if set(row.get('payload', {}).get('gap_ids', [])) - known_gaps: errors.append(f'{row["id"]}: unknown gap ID')
    cases = load_rows(package / 'evaluation/retrieval_cases.jsonl')
    if len({c['id'] for c in cases}) != len(cases): errors.append('Duplicate evaluation case IDs')
    for case in cases:
        if not set(case['expected_record_ids']).issubset(ids): errors.append(f'{case["id"]}: missing expected reference')
        if not case.get('not_for_ingestion'): errors.append(f'{case["id"]}: missing evaluation isolation flag')
    source_file = package / 'evaluation/source-link-check.json'
    source_status = 'not_run'
    if source_file.exists():
        checked = {r['url']: r for r in json.loads(source_file.read_text())['results']}
        used = {u for r in rows for u in r['provenance']}
        pending = [u for u in used if u not in checked or checked[u]['result'] != 'reachable']
        source_status = 'passed_http_reachability' if not pending else 'unconfirmed_urls_remain'
    else:
        pending = []
    return {'passed': not errors, 'record_count': len(rows), 'authored_topics': manifest['authored_topics'],
            'batch_count': len(manifest['batches']), 'gap_sections_mapped': len(coverage), 'evaluation_cases': len(cases),
            'errors': errors, 'source_check': source_status, 'source_urls_unconfirmed': pending,
            'by_language': dict(sorted(Counter(r['metadata']['language'] for r in rows).items())),
            'limitations': ['Structural validation is not expert factual certification.',
                           'Every gap has a dataset or evaluation mapping, not a claim that every gap is closed.',
                           'Existing corpus review, target-specific hardware and live answer quality remain separate work.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=default_package())
    args = parser.parse_args()
    report = validate(args.package.resolve())
    (args.package / 'evaluation/validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
