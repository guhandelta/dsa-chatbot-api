"""Apply reversible local reference hygiene without generating curriculum.

Run from API root: .venv/bin/python -m tools.clean_knowledge_base
Only corpus files and language metadata in knowledge_documents are changed.
No paid calls, model training, exercise execution or approval changes.
"""
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from app.services.knowledge_hygiene import clean_reference_rows, VERSION

API = Path(__file__).resolve().parents[1]
OUTPUT = API.parent / 'reports/knowledge-base-cleanup-2026-10-17'


def write_json(path, value):
    pending = path.with_suffix('.pending')
    pending.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    pending.replace(path)


def write_rows(path, rows):
    pending = path.with_suffix('.pending')
    pending.write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows))
    pending.replace(path)


async def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    library = API / 'data/reference_library'
    rows = [json.loads(line) for line in (library / 'records.jsonl').open() if line.strip()]
    active, quarantine, redirects = clean_reference_rows(rows)
    archive = library / 'quarantine.jsonl'
    previous = [json.loads(line) for line in archive.open() if line.strip()] if archive.exists() else []
    retained = {(q['record']['id'], hashlib.sha256(json.dumps(q['record'], sort_keys=True).encode()).hexdigest()): q
                for q in previous + quarantine}
    write_rows(archive, list(retained.values()))
    write_rows(library / 'records.jsonl', active)
    from app.services.reference_library import eligible
    manifest = json.loads((library / 'manifest.json').read_text())
    manifest.update(record_count=len(active), retrievable_count=sum(eligible(r) for r in active),
                    by_subject=dict(Counter(r['metadata']['subject'] for r in active)),
                    curation_version=VERSION, quarantined_records=len(retained),
                    duplicate_redirects={**manifest.get('duplicate_redirects', {}), **redirects},
                    active_sha256=hashlib.sha256((library / 'records.jsonl').read_bytes()).hexdigest())
    write_json(library / 'manifest.json', manifest)

    # Correct reviewed wording in both retrievable text and explanatory payloads,
    # preserving the original source snapshot and its hash.
    canonical = API / 'data/curriculum/java-javascript.jsonl'
    canonical_rows = [json.loads(line) for line in canonical.open() if line.strip()]
    corrections = []
    rules = {
        'java-tree-path-copy': (
            'A List is passed by reference, so every recursive call shares one path object.',
            'Java passes a copy of the List reference by value. These recursive calls refer to the same mutable path object; rebinding a parameter would not rebind the caller\'s variable.',
            'https://docs.oracle.com/javase/tutorial/java/javaOO/arguments.html'),
        'java-ref-maps-curriculum-levels-p1': (
            'every map lesson depends on `equals` and `hashCode`',
            'hash-based maps depend on `equals` and `hashCode`, while ordered maps such as `TreeMap` determine key equivalence through their ordering comparison',
            'https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html'),
        'js-ref-linkedlists-when-it-must-be-a-linked-list-an-t9': (
            'Contiguous memory is far faster to walk',
            'Typed arrays expose contiguous buffer elements; ordinary Array storage and traversal performance depend on the engine and representation. Measure the relevant workload.',
            'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray'),
    }
    def replace_payload(value, old, new):
        if isinstance(value, str):
            return value.replace(old, new)
        if isinstance(value, list):
            return [replace_payload(v, old, new) for v in value]
        if isinstance(value, dict):
            return {k: replace_payload(v, old, new) for k, v in value.items()}
        return value
    for row in canonical_rows:
        if row['id'] not in rules:
            continue
        old, new, source = rules[row['id']]
        if old in row['document']:
            row['document'] = row['document'].replace(old, new)
            row['payload'] = replace_payload(row['payload'], old, new)
            row['metadata']['correction_source'] = source
            row['metadata']['correction_review'] = '2026-10-17; specific wording correction, not whole-record certification'
            corrections.append(row['id'])
    if corrections:
        write_rows(canonical, canonical_rows)
        cm = API / 'data/curriculum/manifest.json'
        original = json.loads(cm.read_text())
        original['release_sha256'] = hashlib.sha256(canonical.read_bytes()).hexdigest()
        original['correction_review'] = '2026-10-17; argument passing, map equivalence and JS layout wording; original source hash retained'
        write_json(cm, original)

    from sqlalchemy import select
    from app.db.database import SessionLocal
    from app.db.models import KnowledgeDocument
    from app.services.uploaded_knowledge import infer_language, project
    changes, projections = [], []
    async with SessionLocal() as session:
        documents = list((await session.scalars(select(KnowledgeDocument))).all())
        for d in documents:
            inferred = infer_language(d.filename)
            if not d.language and inferred:
                changes.append({'document_id': d.id, 'filename': d.filename,
                                'before_language': d.language, 'after_language': inferred})
                d.language = inferred
            chunks = project(d.id, d.filename, d.text, d.track, d.language)
            projections.append({'filename': d.filename, 'status': d.status, 'language': d.language,
                                'reference_chunks': len(chunks)})
        await session.commit()

    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'curation_version': VERSION,
              'input_reference_records': len(rows), 'active_reference_records': len(active),
              'newly_archived': len(quarantine), 'total_archive_records': len(retained),
              'new_archive_reasons': dict(Counter(q['reason'] for q in quarantine)),
              'canonical_corrections': corrections, 'upload_metadata_changes': changes,
              'upload_projections': projections,
              'scope': 'Local reference hygiene. Original documents/approvals, private exercise candidates and account data unchanged.'}
    # Preserve the first run's before/after evidence on repeat invocation.
    path = OUTPUT / 'cleanup.json'
    write_json(path if not path.exists() else OUTPUT / 'latest-cleanup.json', report)
    print(json.dumps({k: report[k] for k in ('input_reference_records', 'active_reference_records',
                                           'newly_archived', 'total_archive_records')}, indent=2))
    print(f'Upload metadata repairs: {len(changes)}; canonical wording corrections: {len(corrections)}')


if __name__ == '__main__':
    asyncio.run(main())
