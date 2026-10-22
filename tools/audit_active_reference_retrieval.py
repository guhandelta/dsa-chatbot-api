"""Read-only deployed corpus audit; retains exact-ID metrics and reviewed alternatives."""
import json
from datetime import datetime,timezone
from pathlib import Path
from app.services import curriculum_search, reference_library

ROOT=Path(__file__).resolve().parents[2]
# Alternatives reviewed against the actual text, not inferred from keyword matches.
ALTERNATIVES={
 'js-unicode':{'ids':['corpus-js-string-graphemes-intl-segmenter','corpus-js-ref-strings-unicode-track-p1','corpus-js-string-length'],
               'reason':'Explains UTF-16 length, code points, and grapheme segmentation.'},
 'ruby-dp':{'ids':['ref-3dd0c8bbe1a1095fe503a264','ref-8bb1a036fae754c1cfabd3d5'],
            'reason':'Explains the shared Array.new row and the per-row block constructor.'},
 'ts-assert':{'ids':['ref-ce31ae25839685d1913c87d4'],
              'reason':'Explicitly says as User performs no runtime validation; recommends unknown and shape checking.'},
}

def main():
    package=ROOT/'Training Data/generated/knowledge-gap-fill-v1'
    cases=[json.loads(l) for l in (package/'evaluation/retrieval_cases.jsonl').open() if l.strip()]
    results=[]
    for c in cases:
        subject=None if c['subject']==c['language'] else c['subject']
        docs=curriculum_search.search(c['question'],'language',c['language'],subject=subject)
        ids=[d.metadata.get('problem_id') for d in docs]
        alternative=ALTERNATIVES.get(c['id'],{})
        results.append({'case_id':c['id'],'exact_expected':bool(set(ids)&set(c['expected_record_ids'])),
                        'reviewed_alternative':bool(set(ids)&set(alternative.get('ids',[]))),
                        'alternative_review':alternative,'retrieved_ids':ids,
                        'scope_safe':all(d.metadata.get('language')==c['language'] and d.metadata.get('contains_answer') is False
                            and d.metadata.get('subject',c['language'])==c['subject'] for d in docs)})
    rows=reference_library.records();active={r['id']:r for r in rows}
    candidates=[json.loads(l) for l in (package/'all_records.jsonl').open() if l.strip()]
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'mode':'active_local_corpus_no_overlay',
            'active_records':len(rows),'eligible_records':sum(reference_library.eligible(r) for r in rows),
            'generated_records_intact':all(r['id'] in active and active[r['id']]['document']==r['document'] and reference_library.eligible(active[r['id']]) for r in candidates),
            'cases':len(results),'exact_expected_at_4':sum(r['exact_expected'] for r in results),
            'exact_or_reviewed_alternative_at_4':sum(r['exact_expected'] or r['reviewed_alternative'] for r in results),
            'scope_safety_passed':all(r['scope_safe'] for r in results),
            'unresolved_cases':[r['case_id'] for r in results if not (r['exact_expected'] or r['reviewed_alternative'])],
            'limitations':['Alternative relevance was reviewed for three cases; no blanket relabelling of misses.',
                           'Retrieval relevance does not certify live answers or all corpus facts.'],
            'results':results}
    out=ROOT/'reports/knowledge-base-training-2026-10-18/active-retrieval-recheck.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))

if __name__=='__main__':main()
