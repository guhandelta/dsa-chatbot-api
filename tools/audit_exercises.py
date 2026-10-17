"""Execute all current JS/Java exercise references; report teaching-only material.

Usage: .venv/bin/python -m tools.audit_exercises --output docs/exercise-audit.json
Exit 1 means at least one exercise is blocked. Does not call an LLM or spend credits.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.content_catalog import list_content
from app.services.content_verification import verify_reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    exercises, reference_only = [], []
    for item in list_content():
        if item.track not in ('dsa', 'language', 'algorithm'):
            continue
        if item.language and item.language not in ('java', 'javascript'):
            continue
        if not item.has_tests and item.track != 'dsa':
            reference_only.append(item.id)
            continue
        languages = [item.language] if item.language else ['javascript', 'java']
        for language in languages:
            result = verify_reference(item.id, language)
            exercises.append({'id': item.id, 'language': language, **result})
    blocked = [r for r in exercises if not r['verified']]
    from app.services.curriculum import records
    corpus_exercises = [r['id'] for r in records() if r['metadata']['kind'] == 'exercise']
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Current JavaScript/Java executable curriculum and DSA references',
              'limitations': ['Fixture execution does not prove correctness for all inputs.',
                             'Reference-only material and language-switching pathways are not certified by this audit.',
                             'Other language implementations require their own runtime audit.'],
              'verified_count': len(exercises) - len(blocked), 'blocked_count': len(blocked),
              'reference_only_count': len(reference_only),
              'non_executable_corpus_exercise_count': len(corpus_exercises),
              'non_executable_corpus_exercises': corpus_exercises,
              'fixture_case_checks': sum(r.get('case_count', 0) for r in exercises),
              'exercises': exercises, 'reference_only': reference_only}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{len(exercises)-len(blocked)} verified references; {len(blocked)} blocked; {len(reference_only)} reference-only items")
    for row in blocked:
        print(row['id'], row['language'], '; '.join(row['issues']))
    return int(bool(blocked))


if __name__ == '__main__':
    raise SystemExit(main())
