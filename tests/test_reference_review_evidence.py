"""Claim checks are version-bound partial evidence, never blanket certification."""
import json
from app.services import reference_review_evidence as review


def test_claim_review_is_scoped_and_source_edits_expire_it(tmp_path,monkeypatch):
    path=tmp_path/'reviews.json';monkeypatch.setattr(review,'REVIEW_FILE',path)
    path.write_text(json.dumps({'schema_version':1,'reviews':[
        {'source':'library.jsonl','record_id':'a','content_sha256':'original','reviewed_at':'2026-10-29',
         'status':'claims_source_checked','claims':[{'claim':'One checked claim','sources':['https://docs.example.org/spec']}]}]}))
    result=review.claim_review_summary('library.jsonl',{'a':'original','b':'unreviewed'})
    assert result['records_with_checked_claims']==1 and result['claims_checked']==1
    assert result['eligible_reference_records']==2
    assert 'full-record' in result['scope']
    assert review.claim_review_summary('other.jsonl',{'a':'original'})['claims_checked']==0
    result=review.claim_review_summary('library.jsonl',{'a':'changed'})
    assert result['claims_checked']==0 and result['stale_records']==1


def test_claims_without_supporting_sources_do_not_count(tmp_path,monkeypatch):
    path=tmp_path/'reviews.json';monkeypatch.setattr(review,'REVIEW_FILE',path)
    path.write_text(json.dumps({'schema_version':1,'reviews':[
        {'source':'library.jsonl','record_id':'a','content_sha256':'original','status':'claims_source_checked',
         'claims':[{'claim':'No cited source','sources':[]}]}]}))
    assert review.claim_review_summary('library.jsonl',{'a':'original'})['claims_checked']==0
    path.write_text('malformed')
    assert review.claim_review_summary('library.jsonl',{})['evidence_status']=='invalid'
