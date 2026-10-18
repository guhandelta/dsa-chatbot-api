"""Build knowledge-only RAG datasets from the reviewed authoring files.

No model or embedding calls. Files remain candidates until explicitly imported.
"""
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'Training Data/generated/knowledge-gap-fill-v1'
GAPS = ROOT / 'reports/knowledge-base-cleanup-2026-10-17/REMAINING_SECTIONS_BY_LANGUAGE.md'
LANGUAGE_NOTES = {
    'java': 'Apply this contract through explicit interfaces or ordinary functions as appropriate; identify collection, comparator and resource-owner types in Java examples.',
    'javascript': 'Functions and objects can express this design; account for Number precision, reference sharing, Unicode code units and host-specific resource APIs.',
    'python': 'Use functions, protocols or small classes as appropriate; account for iterator exhaustion, shared mutable containers and explicit context-manager cleanup.',
    'c': 'Represent ownership and callbacks explicitly using structs and function pointers; check bounds, arithmetic, allocation failure and cleanup on every exit path.',
    'cpp': 'Use RAII owners and appropriate value or polymorphic abstractions; document move behavior, iterator invalidation and exception guarantees.',
    'rust': 'Express ownership and borrowing in signatures and choose enum, trait or closure representations; document fallible operations and shared-state synchronization.',
    'ruby': 'Blocks, callable objects, modules and native Enumerators can express the design; account for mutation, Hash-key stability and implementation-dependent recursion capacity.',
    'typescript': 'Use functions, structural interfaces and discriminated unions as appropriate; validate external data because type annotations are erased at runtime.',
    'go': 'Use functions, small interfaces and explicit error results; document goroutine/resource ownership and shared slice/map storage.',
    'csharp': 'Use delegates, interfaces, records and IEnumerable as appropriate; document equality, deferred execution, disposal and Task cancellation contracts.',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_gaps():
    result = []
    section = None
    counts = Counter()
    snapshot = PACKAGE / 'gap-register-snapshot.md'
    for line in (snapshot if snapshot.exists() else GAPS).read_text().split('\n'):
        if line.startswith('## '):
            section = line[3:]
        if line.startswith('- **') and section not in ('Status meaning', 'Evidence'):
            key = {'C++': 'cpp', 'C#': 'csharp', 'CSS and styling frameworks': 'styling'}.get(section, section.lower().replace(' ', '-'))
            counts[key] += 1
            result.append({'gap_id': f'{key}-{counts[key]:02}', 'section': section, 'description': line[2:]})
        elif line.startswith('- ') and section == 'Shared reference gaps':
            counts['shared'] += 1
            result.append({'gap_id': f'shared-{counts["shared"]:02}', 'section': section, 'description': line[2:]})
    return result


def build():
    if not (PACKAGE / 'gap-register-snapshot.md').exists():
        (PACKAGE / 'gap-register-snapshot.md').write_bytes(GAPS.read_bytes())
    rows = []
    for path in sorted((PACKAGE / 'sources').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        header, *sections = re.split(r'^## ', text, flags=re.M)
        config = dict(re.findall(r'^(Language|Subject|Baseline): (.+)$', header, re.M))
        for section in sections:
            heading, body = section.split('\n', 1)
            title, gaps = heading.split(' | ')
            urls = re.findall(r'^Source: (https://\S+)$', body, re.M)
            content = re.sub(r'^Source: https://\S+\n?', '', body, flags=re.M).strip()
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            rid = f'ref-gapfill-v1-{config["Subject"]}-{slug}'
            metadata = {'language': config['Language'], 'subject': config['Subject'], 'kind': 'reference',
                        'track': 'language', 'source': 'reference-library', 'origin': f'generated/knowledge-gap-fill-v1/sources/{path.name}',
                        'contains_answer': False, 'verified': False, 'executable': False,
                        'review_status': 'draft_source_linked_requires_review', 'baseline': config['Baseline'],
                        'doc_url': urls[0] if urls else '', 'dataset_version': 'knowledge-gap-fill-v1',
                        'title': title, 'coverage_scope': 'knowledge-reference', 'authored_on': '2026-10-18'}
            document = f'{title}\nBaseline: {config["Baseline"]}\n\n{content}\n\nPrimary sources:\n' + '\n'.join(urls)
            row = {'id': rid, 'document': document, 'metadata': metadata, 'provenance': urls,
                   'payload': {'gap_ids': [g.strip() for g in gaps.split(',')], 'source_file': path.name,
                               'content_sha256': digest(document.encode()), 'review_required': True}}
            if config['Language'] == 'all':
                from copy import deepcopy
                for language, note in LANGUAGE_NOTES.items():
                    variant = deepcopy(row)
                    variant['id'] = rid.replace('-shared-', f'-{language}-shared-')
                    variant['metadata'].update(language=language, subject=language, shared_concept_id=rid)
                    variant['document'] += f'\n\nLanguage adaptation ({language}): {note}'
                    variant['payload']['content_sha256'] = digest(variant['document'].encode())
                    rows.append(variant)
            else:
                rows.append(row)
    # Include the fourteen earlier records so the delivery is self-contained.
    for filename in ('generated_batch_001.jsonl', 'generated_batch_002.jsonl'):
        for line in (ROOT / 'dsa-chatbot-api/data/reference_library' / filename).open():
            if not line.strip(): continue
            row = json.loads(line)
            urls = row['metadata'].pop('provenance')
            row['provenance'] = urls
            row['metadata']['dataset_version'] = 'knowledge-gap-fill-v1'
            row['metadata']['doc_url'] = urls[0]
            row['metadata']['review_status'] = 'draft_source_linked_requires_review'
            row['metadata']['baseline'] = 'Earlier source-linked batch; release-specific behavior requires review'
            row['payload'] = {'gap_ids': [], 'prior_batch': filename, 'review_required': True}
            rows.append(row)
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate IDs')
    out = PACKAGE / 'batches'
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('*.jsonl'): old.unlink()
    batches = []
    for subject in sorted({r['metadata']['subject'] for r in rows}):
        subset = [r for r in rows if r['metadata']['subject'] == subject]
        path = out / f'{subject}.jsonl'
        raw = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in subset).encode()
        path.write_bytes(raw)
        batches.append({'subject': subject, 'language': subset[0]['metadata']['language'], 'path': f'batches/{path.name}',
                        'records': len(subset), 'sha256': digest(raw), 'status': 'candidate'})
    combined = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows).encode()
    (PACKAGE / 'all_records.jsonl').write_bytes(combined)
    cases = []
    scenario_path = PACKAGE / 'evaluation/scenarios.tsv'
    if scenario_path.exists():
        for case in csv.DictReader(scenario_path.open(), delimiter='\t'):
            expected = [r['id'] for r in rows if r['metadata'].get('title') == case['expected_title']
                        and r['metadata']['language'] == case['language'] and r['metadata']['subject'] == case['subject']]
            if len(expected) != 1: raise ValueError(f'Expected one reference for evaluation {case["id"]}: {expected}')
            cases.append({'id': case['id'], 'language': case['language'], 'subject': case['subject'],
                          'question': case['question'], 'expected_record_ids': expected,
                          'required_concepts_for_human_answer_review': case['required_concepts'].split(';'),
                          'evaluation_only': True, 'not_for_ingestion': True})
        (PACKAGE / 'evaluation/retrieval_cases.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cases))
    gaps = read_gaps()
    with (PACKAGE / 'coverage.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['gap_id', 'section', 'description', 'record_count', 'record_ids', 'status'])
        writer.writeheader()
        for gap in gaps:
            matched = [r['id'] for r in rows if gap['gap_id'] in r.get('payload', {}).get('gap_ids', [])]
            status = 'supplement_created_review_pending' if matched else 'unmapped'
            if gap['gap_id'] in ('shared-01', 'shared-02', 'shared-03'):
                matched = [r['id'] for r in rows if r['id'].startswith('ref-gapfill-')]
                status = 'new_record_metadata_and_prose_added_legacy_review_pending'
            if 'needs factual review' in gap['description']:
                status = 'new_guidance_added_legacy_claim_review_pending' if matched else 'unmapped'
            if gap['gap_id'] in ('python-07', 'c-04'):
                status = 'portable_guidance_added_target_specific_details_pending'
            if gap['gap_id'] == 'shared-06':
                matched = ['evaluation/retrieval_cases.jsonl']
                status = 'retrieval_evaluation_cases_created_not_run'
            writer.writerow({**gap, 'record_count': len(matched), 'record_ids': '|'.join(matched),
                             'status': status})
    manifest = {'version': 'knowledge-gap-fill-v1', 'created_on': '2026-10-18', 'purpose': 'knowledge-only RAG ingestion',
                'record_count': len(rows), 'new_records': sum(r['id'].startswith('ref-gapfill-') for r in rows),
                'prior_records': 14, 'authored_topics': sum(1 for p in (PACKAGE / 'sources').glob('*.md') for l in p.read_text().split('\n') if l.startswith('## ')),
                'shared_concepts_exported_per_language': 8, 'batches': batches, 'all_records_sha256': digest(combined),
                'coverage_sections': len(gaps), 'training_state': 'candidate_files_only',
                'review_status': 'not_expert_certified', 'embedding_calls': 0, 'model_training_calls': 0,
                'source_note': 'Links are provenance pointers; link presence is not evidence of claim certification.'}
    manifest['retrieval_evaluation_cases'] = len(cases)
    manifest['gap_register_sha256'] = digest((PACKAGE / 'gap-register-snapshot.md').read_bytes())
    (PACKAGE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    c_source = (PACKAGE / 'sources/13-c.md').read_text()
    c_example = re.search(r'```c\n(.*?)\n```', c_source, re.S).group(1)
    (PACKAGE / 'examples').mkdir(exist_ok=True)
    (PACKAGE / 'examples/graph_atomic_insert.c').write_text(c_example + '\n')
    index = ['# Dataset index', '', '| Subject | Language | Records | File |', '| --- | --- | ---: | --- |']
    index.extend(f'| {b["subject"]} | {b["language"]} | {b["records"]} | [{b["path"]}]({b["path"]}) |' for b in batches)
    (PACKAGE / 'DATASET_INDEX.md').write_text('\n'.join(index) + '\n')
    for filename, export in [('validate_gap_training_datasets.py', 'validate_dataset.py'),
                             ('import_gap_training_datasets.py', 'import_dataset.py'),
                             ('evaluate_gap_dataset_retrieval.py', 'evaluate_retrieval.py'),
                             ('check_gap_dataset_sources.py', 'check_sources.py')]:
        tool = ROOT / 'dsa-chatbot-api/tools' / filename
        if tool.exists():
            (PACKAGE / 'tools').mkdir(exist_ok=True)
            (PACKAGE / 'tools' / export).write_bytes(tool.read_bytes())
    files = [p for p in sorted(PACKAGE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ('SHA256SUMS', '.DS_Store')]
    (PACKAGE / 'SHA256SUMS').write_text(''.join(f'{digest(p.read_bytes())}  {p.relative_to(PACKAGE).as_posix()}\n' for p in files))
    archive = PACKAGE.parent / 'knowledge-gap-fill-v1.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(PACKAGE.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.name != '.DS_Store':
                z.write(path, str(Path(PACKAGE.name) / path.relative_to(PACKAGE)))
    print(json.dumps({'records': len(rows), 'batches': len(batches), 'gap_sections': len(gaps), 'archive': str(archive)}, indent=2))


if __name__ == '__main__':
    build()
