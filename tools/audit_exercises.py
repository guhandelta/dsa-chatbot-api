"""Execute function-based curriculum references for supported languages.

Usage: .venv/bin/python -m tools.audit_exercises --output docs/exercise-audit.json
       .venv/bin/python -m tools.audit_exercises --language typescript --output /tmp/ts-audit.json
Exit 1 means at least one exercise is blocked. Does not call an LLM or spend credits.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.content_catalog import list_content
from app.services.content_verification import verify_reference
from app.services.execution_adapters import ADAPTERS

FUNCTION_LANGUAGES = tuple(
    language for language, adapter in ADAPTERS.items() if adapter.function_tests
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--language', choices=FUNCTION_LANGUAGES, action='append',
                        help='Audit one language instead of every function-test language.')
    parser.add_argument('--publish-evidence',action='store_true',help='Record version-bound execution outcomes for the dashboard')
    parser.add_argument('--workers',type=int,default=1,choices=range(1,5),help='At most four isolated execution jobs')
    args = parser.parse_args()
    exercises, reference_only, tasks = [], [], []
    languages = tuple(dict.fromkeys(args.language)) if args.language else FUNCTION_LANGUAGES
    for item in list_content():
        if item.track not in ('dsa', 'language', 'algorithm'):
            continue
        if item.language and item.language not in languages:
            continue
        if not item.has_tests and item.track != 'dsa':
            scoped = (item.language,) if item.language else languages
            reference_only.extend(f'{item.id}:{language}' for language in scoped)
            continue
        item_languages = (item.language,) if item.language else languages
        for language in item_languages:
            tasks.append((item.id,language))
    from app.services.code_runner import available_languages
    from app.services.verification_evidence import verifier_fingerprint
    initial_profile=verifier_fingerprint()
    available_languages()  # Warm container toolchain detection before parallel work.
    def execute(task):
        content_id,language=task
        return {'id':content_id,'language':language,**verify_reference(content_id,language)}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(execute,tasks):
            exercises.append(result)
            print(f"{result['id']} [{result['language']}]: {'passed' if result['verified'] else 'needs attention'}",flush=True)
    blocked = [r for r in exercises if not r['verified']]
    from app.services.curriculum import records
    corpus_exercises = [r['id'] for r in records() if r['metadata']['kind'] == 'exercise']
    summary = {}
    for language in languages:
        rows = [row for row in exercises if row['language'] == language]
        summary[language] = {
            'verified': sum(bool(row['verified']) for row in rows),
            'blocked': sum(not row['verified'] for row in rows),
            'fixture_case_checks': sum(row.get('case_count', 0) for row in rows),
            'reference_only': sum(row.endswith(f':{language}') for row in reference_only),
        }
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Function-test curriculum and DSA references by language',
              'languages': list(languages),
              'language_summary': summary,
              'limitations': ['Fixture execution does not prove correctness for all inputs.',
                             'Reference-only material and framework pathways are not certified by this audit.',
                             'Framework behavior requires separate dependency-aware project tests.'],
              'verified_count': len(exercises) - len(blocked), 'blocked_count': len(blocked),
              'reference_only_count': len(reference_only),
              'non_executable_corpus_exercise_count': len(corpus_exercises),
              'non_executable_corpus_exercises': corpus_exercises,
              'fixture_case_checks': sum(r.get('case_count', 0) for r in exercises),
              'exercises': exercises, 'reference_only': reference_only}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    if args.publish_evidence:
        from app.services.verification_evidence import publish_execution
        if verifier_fingerprint()!=initial_profile:
            raise RuntimeError('Verifier changed during the audit; rerun before publishing evidence')
        print(f'Published {publish_execution(report)} execution checks',flush=True)
    print(f"{len(exercises)-len(blocked)} verified references; {len(blocked)} blocked; {len(reference_only)} reference-only items")
    for row in blocked:
        print(row['id'], row['language'], '; '.join(row['issues']))
    return int(bool(blocked))


if __name__ == '__main__':
    raise SystemExit(main())
