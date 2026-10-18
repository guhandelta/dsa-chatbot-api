"""Read-only evaluation using the app's actual local retriever and candidate overlay."""
import argparse
import json
import sys
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    local = Path(__file__).resolve().parents[1]
    package = local if (local / 'manifest.json').exists() else local.parent / 'Training Data/generated/knowledge-gap-fill-v1'
    parser.add_argument('--package', type=Path, default=package)
    parser.add_argument('--api-root', type=Path, required=True)
    parser.add_argument('--candidate-only', action='store_true')
    args = parser.parse_args()
    package = args.package.resolve()
    sys.path.insert(0, str(args.api_root.resolve()))
    from app.services import reference_library as library
    from app.services import curriculum_search as retriever
    candidates = [json.loads(line) for line in (package / 'all_records.jsonl').open() if line.strip()]
    cases = [json.loads(line) for line in (package / 'evaluation/retrieval_cases.jsonl').open() if line.strip()]
    current = [] if args.candidate_only else library.records()
    overlay = {r['id']: r for r in current}
    for row in candidates:
        if row['id'] in overlay and row['document'] != overlay[row['id']]['document']:
            raise SystemExit('Conflicting document in overlay: ' + row['id'])
        overlay[row['id']] = row
    stat = (package / 'all_records.jsonl').stat()
    results = []
    retriever._index.cache_clear()
    with patch.object(library, 'records', return_value=list(overlay.values())), patch.object(library, 'version', return_value=(str(package), stat.st_mtime_ns, stat.st_size)):
        for case in cases:
            # Core language queries use the same general-tutor route, including
            # canonical competitors. Framework queries retain explicit scope.
            subject = None if case['subject'] == case['language'] else case['subject']
            hits = retriever.search(case['question'], 'language', case['language'], k=4, subject=subject)
            ids = [h.metadata.get('problem_id') for h in hits]
            rank = next((i + 1 for i, rid in enumerate(ids) if rid in case['expected_record_ids']), None)
            isolation = all(h.metadata.get('language') == case['language'] and h.metadata.get('contains_answer') is False
                            and (not subject or h.metadata.get('subject') == subject) for h in hits)
            results.append({'case_id': case['id'], 'found_in_top_4': rank is not None, 'rank': rank,
                            'scope_and_answer_safety_passed': isolation, 'retrieved_ids': ids,
                            'expected_ids': case['expected_record_ids']})
    retriever._index.cache_clear()
    found = sum(r['found_in_top_4'] for r in results)
    report = {'mode': 'candidate_overlay_actual_app_local_BM25', 'existing_library_included': not args.candidate_only,
              'cases': len(results), 'found_in_top_4': found, 'recall_at_4': found / max(1, len(results)),
              'mean_reciprocal_rank_at_4': sum(1 / r['rank'] if r['rank'] else 0 for r in results) / max(1, len(results)),
              'scope_and_answer_safety_passed': all(r['scope_and_answer_safety_passed'] for r in results),
              'writes_to_live_corpus': 0, 'embedding_calls': 0, 'model_calls': 0,
              'limitations': ['This is a finite authored retrieval probe, not independent answer correctness certification.',
                             'No HTTP, semantic-vector, subscription-policy, or live LLM-answer evaluation.'],
              'results': results}
    (package / 'evaluation/retrieval-preview.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, indent=2))
    print('Retrieval misses:', ', '.join(r['case_id'] for r in results if not r['found_in_top_4']))
    raise SystemExit(0 if report['scope_and_answer_safety_passed'] else 1)


if __name__ == '__main__':
    main()
