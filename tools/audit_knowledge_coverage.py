"""Read-only inventory and evidence audit of EVERY packaged language/subject.

No provider calls, code execution, ingestion, approvals or balance changes.
Topic matches are discovery evidence, NEVER a completeness/correctness score.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# A review checklist, not a prescribed curriculum or an exhaustive language spec.
TOPICS = {
    'values-types': r'\b(?:types?|variables?|values?)\b',
    'control-flow': r'\b(?:loops?|conditional|branching|control flow)\b',
    'functions': r'\b(?:functions?|methods?|parameters?|arguments?)\b',
    'collections': r'\b(?:arrays?|lists?|collections?|vectors?)\b',
    'strings-unicode': r'\b(?:strings?|unicode|encoding)\b',
    'errors': r'\b(?:exceptions?|error handling|result type|panic)\b',
    'modules-dependencies': r'\b(?:modules?|packages?|dependencies|imports?)\b',
    'testing-debugging': r'\b(?:tests?|testing|debugging|debugger)\b',
    'references-memory': r'\b(?:references?|ownership|pointers?|garbage collection|lifetimes?)\b',
    'equality-ordering': r'\b(?:equality|ordering|comparator|hashing|hashcode)\b',
    'complexity': r'\b(?:complexity|big.o|asymptotic)\b',
    'recursion': r'\b(?:recursion|recursive|base case)\b',
    'search-sort': r'\b(?:binary search|sorting|quicksort|mergesort)\b',
    'linked-lists': r'\b(?:linked lists?|linkedlist|node references?)\b',
    'stacks-queues': r'\b(?:stacks?|queues?|deques?)\b',
    'trees-heaps': r'\b(?:trees?|heaps?|tries?)\b',
    'graphs': r'\b(?:graphs?|vertices|edges|breadth.first|depth.first)\b',
    'dynamic-programming': r'\b(?:dynamic programming|memoization|tabulation)\b',
    'greedy-backtracking': r'\b(?:greedy|backtracking)\b',
    'boundary-cases': r'\b(?:edge cases?|boundary|overflow|underflow|empty input)\b',
}


def summarize(rows):
    groups = defaultdict(list)
    errors, seen = [], set()
    for collection, row in rows:
        rid = row.get('id')
        if not rid or (collection, rid) in seen:
            errors.append({'collection': collection, 'id': rid, 'issue': 'missing_or_duplicate_id'})
        seen.add((collection, rid))
        m = row.get('metadata', {})
        if not m.get('language') or not isinstance(m.get('contains_answer'), bool):
            errors.append({'collection': collection, 'id': rid, 'issue': 'missing_language_or_explicit_answer_flag'})
        if any(not isinstance(v, (str, bool, int, float)) for v in m.values()):
            errors.append({'collection': collection, 'id': rid, 'issue': 'non_scalar_metadata'})
        if not isinstance(row.get('document'), str) or not row.get('document', '').strip():
            errors.append({'collection': collection, 'id': rid, 'issue': 'missing_document'})
        if collection == 'reference_library' and not row.get('provenance'):
            errors.append({'collection': collection, 'id': rid, 'issue': 'missing_provenance'})
        if m.get('kind') in ('exercise', 'gotcha') and m.get('contains_answer') is False:
            errors.append({'collection': collection, 'id': rid, 'issue': 'answer_bearing_kind_marked_safe'})
        groups[(m.get('language', 'unknown'), m.get('subject') or m.get('language', 'unknown'))].append(row)
    subjects = []
    for (language, subject), items in sorted(groups.items()):
        # Deliberately inspect learner reference text only; private solutions must
        # not inflate evidence that a topic is actually available to the learner.
        from app.services.knowledge_hygiene import PUBLIC_REFERENCE_KINDS
        safe = [r for r in items if r['metadata'].get('contains_answer') is False
                and r['metadata'].get('kind') in PUBLIC_REFERENCE_KINDS]
        evidence = {topic: [r['id'] for r in safe if re.search(pattern, r['document'], re.I)][:3]
                    for topic, pattern in TOPICS.items()}
        subjects.append({'language': language, 'subject': subject, 'records': len(items),
            'reference_safe_records': len(safe), 'by_kind': dict(Counter(r['metadata']['kind'] for r in items)),
            'candidate_exercises': sum(r['metadata']['kind'] == 'exercise' for r in items),
            'explicit_version_metadata_records': sum(any(k in r['metadata'] for k in
                ('version', 'runtime_version', 'rust_edition', 'framework_version')) for r in items),
            'topic_evidence_ids': evidence,
            'topics_not_evidenced_by_scan': [k for k, v in evidence.items() if not v],
            'quality_status': 'not_certified',
            'scope_note': 'Keyword matches are review leads, not evidence of completeness or factual correctness. Framework subjects need framework-specific review.'})
    return {'records': len(rows), 'languages': sorted({s['language'] for s in subjects}),
            'subjects': subjects, 'structural_findings': errors}


def audit():
    from app.services import content_catalog as catalog
    from app.services.code_runner import _TOOLCHAIN
    from app.services.curriculum_search import search
    rows, hashes = [], {}
    for collection, relative in [('canonical', 'data/curriculum/java-javascript.jsonl'),
                                 ('reference_library', 'data/reference_library/records.jsonl')]:
        path = ROOT / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Iterating actual newline records preserves Unicode U+2028/U+2029 in strings.
        rows.extend((collection, json.loads(line)) for line in path.open(encoding='utf-8') if line.strip())
    report = summarize(rows)
    authored = catalog.list_content()
    for subject in report['subjects']:
        language, name = subject['language'], subject['subject']
        probes = []
        framework_queries = {
            'spring-core': ('dependency injection beans', 'application context lifecycle', 'configuration scopes'),
            'spring-boot': ('auto configuration', 'configuration properties', 'application testing'),
            'spring-mvc': ('DispatcherServlet controllers', 'request mapping validation', 'exception handling'),
            'spring-data': ('repository persistence', 'transactions queries', 'entity mapping'),
            'spring-security': ('authentication authorization', 'filter chain', 'CSRF security testing'),
            'spring-testing': ('unit integration testing', 'test slices', 'mock application context'),
            'python-django': ('Django models ORM', 'request views routing', 'testing migrations'),
            'python-fastapi': ('FastAPI dependency injection', 'request validation asynchronous', 'testing responses'),
            'python-flask': ('Flask application context', 'request routing blueprints', 'testing configuration'),
            'embedded-c': ('interrupt memory register', 'pointer volatile', 'peripheral testing'),
            'embedded-python': ('interrupt memory allocation', 'MicroPython peripherals', 'hardware timing'),
        }
        queries = framework_queries.get(name, ('variables functions types', 'collections equality memory', 'binary search graph traversal'))
        for query in queries:
            docs = search(query, 'language', language, subject=name if name != language else None)
            scope_ok = all(d.metadata.get('language') == language and d.metadata.get('contains_answer') is False
                           and (d.metadata.get('subject') == name if name != language else
                                d.metadata.get('subject', name) == name) for d in docs)
            probes.append({'query': query, 'result_count': len(docs), 'scope_ok': scope_ok,
                           'source_ids': [d.metadata['problem_id'] for d in docs]})
        subject['retrieval_probes'] = probes
        subject['execution_adapter_available_in_code'] = language in _TOOLCHAIN
        subject['authored_foundation_exercises'] = sum(c.track == 'language' and c.language == language and c.has_tests for c in authored) if name == language else 0
        subject['application_reference_extractor_supported'] = language in ('python', 'javascript', 'java')
        subject['learner_reference_admission_gate_enabled'] = language in ('javascript', 'java')
    solution_sections = Counter()
    for c in authored:
        if c.track == 'dsa':
            path = catalog.find_path(c.id)
            if path:
                solution_sections.update(re.findall(r'^### (Python|JavaScript|Java|C\+\+|C|Rust|Go|Ruby|TypeScript)\s*$', path.read_text(), re.M))
    report.update({'generated_at': datetime.now(timezone.utc).isoformat(), 'corpus_sha256': hashes,
                   'authored_dsa_solution_sections': dict(solution_sections),
                   'limitations': ['No LLM calls or executions occur in this inventory.',
                     'Presence and keyword matches do not verify teaching claims or exercise answers.',
                     'Runtime code support does not prove a runtime is installed or an example passed.',
                     'Actual uploaded PDF contents remain separately covered by uploaded-reference-audit.json.',
                     'This does not restructure learning paths or change subscription/payment policy.']})
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['records']} records, {len(report['languages'])} languages, {len(report['subjects'])} subjects; {len(report['structural_findings'])} structural findings")
    raise SystemExit(int(bool(report['structural_findings']) or any(not p['scope_ok'] for s in report['subjects'] for p in s['retrieval_probes'])))
