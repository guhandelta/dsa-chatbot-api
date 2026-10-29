"""Aggregate explicitly scoped claim reviews; never certify an entire corpus."""
import json
from pathlib import Path

REVIEW_FILE=Path(__file__).resolve().parents[2]/'data/verification/reference-reviews.json'


def claim_review_summary(source,content_hashes):
    status='not_recorded';reviews=[]
    try:
        data=json.loads(REVIEW_FILE.read_text())
        if data.get('schema_version')!=1 or not isinstance(data.get('reviews'),list):
            raise ValueError('Invalid review evidence')
        reviews=data['reviews'];status='available'
    except FileNotFoundError:pass
    except (OSError,ValueError,TypeError,AttributeError):status='invalid';reviews=[]
    current={};stale=set();last=[]
    for review in reviews:
        if not isinstance(review,dict) or review.get('source')!=source:continue
        rid=review.get('record_id')
        if rid not in content_hashes:continue
        if review.get('content_sha256')!=content_hashes[rid]:
            stale.add(rid);continue
        claims=review.get('claims',[])
        if review.get('status')!='claims_source_checked' or not isinstance(claims,list):continue
        valid=[c for c in claims if isinstance(c,dict) and isinstance(c.get('claim'),str)
               and isinstance(c.get('sources'),list) and c['sources']
               and all(isinstance(u,str) and u.startswith('https://') for u in c['sources'])]
        if valid:
            current[rid]=valid
            if isinstance(review.get('reviewed_at'),str):last.append(review['reviewed_at'])
    return {'evidence_status':status,'records_with_checked_claims':len(current),
            'claims_checked':sum(len(v) for v in current.values()),'stale_records':len(stale),
            'eligible_reference_records':len(content_hashes),'last_checked_at':max(last) if last else None,
            'review_method':'Assistant comparison with cited primary documentation',
            'reviewed_claims':[{'record_id':rid,'claims':claims} for rid,claims in list(current.items())[:10]],
            'scope':'Listed claims only; full-record factual certification and teaching review remain unrecorded.'}
