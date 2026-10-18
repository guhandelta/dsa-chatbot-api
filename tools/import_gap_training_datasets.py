"""Dry-run or explicitly merge the dataset into an API's local RAG library."""
import argparse
import importlib.util
import json
import os
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def resolve_validator():
    here = Path(__file__).resolve().parent
    source = here / 'validate_gap_training_datasets.py'
    if not source.exists(): source = here / 'validate_dataset.py'
    spec = importlib.util.spec_from_file_location('dataset_validation', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic_write(path, raw):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.dataset-', delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    validation = resolve_validator()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=validation.default_package())
    parser.add_argument('--api-root', type=Path, required=True)
    parser.add_argument('--subject', action='append', help='Import only selected subject(s); repeatable')
    parser.add_argument('--apply', action='store_true', help='Write files after validation; default is read-only')
    args = parser.parse_args()
    package, api = args.package.resolve(), args.api_root.resolve()
    report = validation.validate(package)
    if not report['passed']: raise SystemExit('Validation failed: ' + '; '.join(report['errors']))
    candidates = validation.load_rows(package / 'all_records.jsonl')
    known = {r['metadata']['subject'] for r in candidates}
    if args.subject and set(args.subject) - known: raise SystemExit('Unknown subject')
    candidates = [r for r in candidates if not args.subject or r['metadata']['subject'] in args.subject]
    target = api / 'data/reference_library/records.jsonl'
    manifest_path = target.with_name('manifest.json')
    original = target.read_bytes()
    manifest_original = manifest_path.read_bytes()
    existing = validation.load_rows(target)
    by_id = {r['id']: r for r in existing}
    new, skipped = [], []
    for row in candidates:
        old = by_id.get(row['id'])
        if old is None:
            new.append(row)
        elif (old['document'], old['metadata']['language'], old['metadata']['subject']) == (row['document'], row['metadata']['language'], row['metadata']['subject']):
            skipped.append(row['id'])
        else:
            raise SystemExit(f'Conflicting existing ID {row["id"]}; refusing to overwrite')
    result = {'mode': 'apply' if args.apply else 'dry_run', 'candidate_records': len(candidates), 'new_records': len(new),
              'identical_records_skipped': len(skipped), 'source_check': report['source_check'],
              'integration': 'packaged_local_lexical_RAG', 'embedding_calls': 0, 'model_training_calls': 0,
              'review_status': 'draft_source_linked_requires_review'}
    if args.apply and new:
        if report['source_check'] != 'passed_http_reachability': raise SystemExit('Resolve source-link checks before applying')
        # A backup plus optimistic concurrency check prevents silent replacement
        # of a corpus edited since this process read it. Run imports sequentially.
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = target.parent / 'import_backups' / stamp
        backup.mkdir(parents=True, mode=0o700)
        (backup.parent / '.gitignore').write_text('*\n')
        shutil.copy2(target, backup / target.name)
        shutil.copy2(manifest_path, backup / manifest_path.name)
        if target.read_bytes() != original or manifest_path.read_bytes() != manifest_original:
            raise SystemExit('Corpus changed during import; retry after other writer finishes')
        merged = existing + new
        manifest = json.loads(manifest_original)
        manifest['record_count'] = len(merged)
        manifest['retrievable_count'] = sum(r['metadata'].get('contains_answer') is False and r['metadata'].get('kind') in ('concept', 'reference') for r in merged)
        manifest['by_subject'] = dict(sorted(Counter(r['metadata']['subject'] for r in merged).items()))
        manifest.setdefault('dataset_imports', []).append({'version': 'knowledge-gap-fill-v1', 'imported_at': stamp,
            'records_added': len(new), 'subjects': sorted({r['metadata']['subject'] for r in new}),
            'integration': 'packaged_local_lexical_RAG', 'embedding_rebuild': 'not_run'})
        try:
            atomic_write(target, ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in merged).encode())
            atomic_write(manifest_path, (json.dumps(manifest, indent=2) + '\n').encode())
        except BaseException:
            atomic_write(target, original)
            atomic_write(manifest_path, manifest_original)
            raise
        result['backup'] = str(backup)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
