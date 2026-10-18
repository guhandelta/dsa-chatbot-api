"""Apply reference-cleanup-v3 to the packaged library without re-reading Training Data.

Run from API root: python3 -m tools.apply_reference_cleanup_v3 [--apply]
Re-chunks extracted documents on headings, from the full text already stored in
each document's first chunk, then applies the shared hygiene policy. Every row
it replaces or removes is appended to quarantine.jsonl with its reason. Without
--apply it writes the would-be files next to the report and changes nothing.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from app.services.knowledge_hygiene import (clean_reference_rows, reference_id, section_chunks, strip_contents,
                                             VERSION)
from tools.import_reference_library import safe_reference

API = Path(__file__).resolve().parents[1]
LIBRARY = API / 'data/reference_library'


def read_rows(path):
    return [json.loads(line) for line in path.open(encoding='utf-8') if line.strip()]


def write_rows(path, rows):
    pending = path.with_suffix('.pending')
    pending.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf-8')
    pending.replace(path)


def is_section_source(row):
    return isinstance(row.get('payload'), dict) and 'source_sha256' in row['payload']


def rechunk(rows, archive):
    full_text = {}
    for row in rows + [q['record'] for q in archive]:
        payload = row.get('payload')
        if is_section_source(row) and payload.get('full_text'):
            full_text.setdefault((row['metadata']['subject'], payload['source_sha256']), payload['full_text'])
    groups = defaultdict(list)
    kept = []
    for row in rows:
        key = (row['metadata']['subject'], row['payload']['source_sha256']) if is_section_source(row) else None
        # Rows already chunked on headings are left as they are, so reruns change nothing.
        if key in full_text and row['payload'].get('chunking') != 'heading-sections-v1':
            groups[key].append(row)
        else:
            kept.append(row)
    created, replaced = [], []
    for (subject, sha), old in sorted(groups.items()):
        first = min(old, key=lambda r: r['id'])
        provenance = sorted({p for r in old for p in r['provenance']})
        for i, part in enumerate(section_chunks(safe_reference(strip_contents(full_text[(subject, sha)])))):
            created.append({'id': reference_id(subject, 'section-' + sha + '-' + str(i)), 'document': part,
                'metadata': {'source': 'reference-library', 'kind': 'reference', 'language': first['metadata']['language'],
                             'subject': subject, 'track': 'language', 'contains_answer': False, 'verified': False,
                             'executable': False, 'origin': first['metadata']['origin']},
                'provenance': provenance,
                'payload': {'source_sha256': sha, 'full_text': full_text[(subject, sha)] if i == 0 else '',
                            'verification': 'not_executed', 'chunking': 'heading-sections-v1'}})
        replaced.extend({'reason': 'Fixed-size chunk replaced by heading-scoped sections of the same source text.',
                         'record': r} for r in old)
    return kept + created, replaced, len(groups)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--out', type=Path, default=API.parent / 'reports/kb-audit-fix-2026-10-18/dry-run')
    args = parser.parse_args()
    rows = read_rows(LIBRARY / 'records.jsonl')
    archive = read_rows(LIBRARY / 'quarantine.jsonl')
    staged, replaced, documents = rechunk(rows, archive)
    active, quarantine, redirects = clean_reference_rows(staged)
    ids = Counter(r['id'] for r in active)
    clashes = [i for i, n in ids.items() if n > 1]
    if clashes:
        raise SystemExit(f'{len(clashes)} duplicate IDs after cleanup, e.g. {clashes[:3]}; nothing written')
    retained = {(q['record']['id'], hashlib.sha256(json.dumps(q['record'], sort_keys=True).encode()).hexdigest()): q
                for q in archive + replaced + quarantine}
    from app.services.reference_library import eligible
    reasons = Counter(q['reason'] for q in replaced + quarantine)
    summary = {'curation_version': VERSION, 'records_before': len(rows), 'records_after': len(active),
               'retrievable_after': sum(eligible(r) for r in active), 'documents_rechunked': documents,
               'archived_this_run': len(replaced) + len(quarantine), 'archive_after': len(retained),
               'archived_by_reason': dict(reasons.most_common())}
    target = LIBRARY if args.apply else args.out
    target.mkdir(parents=True, exist_ok=True)
    write_rows(target / 'records.jsonl', active)
    write_rows(target / 'quarantine.jsonl', list(retained.values()))
    manifest = json.loads((LIBRARY / 'manifest.json').read_text())
    manifest.update(record_count=len(active), retrievable_count=summary['retrievable_after'],
                    by_subject=dict(Counter(r['metadata']['subject'] for r in active)),
                    curation_version=VERSION, quarantined_records=len(retained),
                    duplicate_redirects={**manifest.get('duplicate_redirects', {}), **redirects},
                    active_sha256=hashlib.sha256((target / 'records.jsonl').read_bytes()).hexdigest())
    manifest.setdefault('maintenance', []).append({'command': 'tools.apply_reference_cleanup_v3', **summary})
    pending = target / 'manifest.pending'
    pending.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    pending.replace(target / 'manifest.json')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
