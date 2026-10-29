"""A past passing run must never certify changed content, a failure or prose."""
import hashlib
import json
from pathlib import Path
import pytest
from app.services import verification_evidence as evidence


@pytest.fixture
def workspace(tmp_path,monkeypatch):
    root=tmp_path/'data';root.mkdir();path=root/'lesson.md';path.write_text('# Lesson\n')
    monkeypatch.setattr(evidence,'DATA_DIR',root)
    monkeypatch.setattr(evidence,'EVIDENCE_FILE',root/'verification/execution.json')
    monkeypatch.setattr(evidence,'verifier_fingerprint',lambda:'profile-one')
    monkeypatch.setattr('app.services.content_catalog.find_path',lambda _:path)
    return path


def result(path,verified=True,status='passed'):
    return {'checked_at':'2026-10-29T00:00:00+00:00','exercises':[
        {'id':'lesson','language':'python','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'verified':verified,'case_count':6,'issues':[],
         'execution':{'can_publish':verified,'unverified':[],'results':[{'status':status}]}}]}


def test_real_pass_is_recorded_and_source_edit_invalidates_it(workspace):
    evidence.publish_execution(result(workspace))
    summary=evidence.execution_summary([workspace])
    assert summary['passed']==1 and summary['fixture_case_checks']==6
    workspace.write_text('# Changed\n')
    summary=evidence.execution_summary([workspace])
    assert summary['passed']==0 and summary['stale']==1 and summary['fixture_case_checks']==0


def test_verifier_change_invalidates_old_pass(workspace,monkeypatch):
    evidence.publish_execution(result(workspace))
    monkeypatch.setattr(evidence,'verifier_fingerprint',lambda:'profile-two')
    assert evidence.execution_summary([workspace])['stale']==1


def test_latest_failure_replaces_pass_and_no_run_cannot_pass(workspace):
    evidence.publish_execution(result(workspace))
    evidence.publish_execution(result(workspace,False,'failed'))
    summary=evidence.execution_summary([workspace])
    assert summary['passed']==0 and summary['failed']==1
    forged=result(workspace);forged['exercises'][0].pop('execution')
    evidence.publish_execution(forged)
    assert evidence.execution_summary([workspace])['blocked']==1
    assert evidence.execution_summary([workspace])['passed']==0


def test_source_changed_before_publication_is_rejected(workspace):
    report=result(workspace);workspace.write_text('# Edited after run')
    with pytest.raises(ValueError,match='Source changed'):evidence.publish_execution(report)
    assert not evidence.EVIDENCE_FILE.exists()


def test_malformed_evidence_is_explicit_and_unrelated_sources_get_no_pass(workspace):
    evidence.publish_execution(result(workspace))
    assert evidence.execution_summary([])['passed']==0
    evidence.EVIDENCE_FILE.write_text('{broken')
    summary=evidence.execution_summary([workspace])
    assert summary['passed']==0 and summary['evidence_status']=='invalid'
    evidence.EVIDENCE_FILE.write_text(json.dumps({'schema_version':1,'checks':[{}]}))
    assert evidence.execution_summary([workspace])['evidence_status']=='invalid'


def test_duplicate_evidence_is_not_double_counted(workspace):
    evidence.publish_execution(result(workspace))
    data=json.loads(evidence.EVIDENCE_FILE.read_text());data['checks']*=2
    evidence.EVIDENCE_FILE.write_text(json.dumps(data))
    assert evidence.execution_summary([workspace])['evidence_status']=='invalid'


def test_inventory_uses_execution_evidence_without_certifying_prose(workspace,monkeypatch):
    from types import SimpleNamespace
    from app.services import knowledge_inventory as inventory
    evidence.publish_execution(result(workspace))
    monkeypatch.setattr(inventory,'DATA_DIR',workspace.parent)
    monkeypatch.setattr(inventory.content_catalog,'_all_dirs',lambda:[workspace.parent])
    monkeypatch.setattr(inventory.content_catalog,'list_content',lambda:[SimpleNamespace(
        source='authored',language='python',track='language',has_tests=True)])
    source=inventory._authored_inventory()
    assert source['execution_evidence']['passed']==1
    assert source['executable_examples']=='tests_passed_for_recorded_cases'
    assert source['quality_status']=='not_certified'
    assert source['factual_review']==source['pedagogical_review']=='not_recorded'
    workspace.write_text('# Updated source')
    source=inventory._authored_inventory()
    assert source['execution_evidence']['passed']==0
    assert source['execution_evidence']['stale']==1
    assert source['executable_examples']=='outdated_evidence'


def test_changed_executor_environment_requires_reverification(workspace,monkeypatch):
    evidence.publish_execution(result(workspace))
    monkeypatch.setattr(evidence.settings,'exec_backend','docker')
    monkeypatch.setattr(evidence.settings,'exec_container_image','sha256:'+'b'*64)
    summary=evidence.execution_summary([workspace])
    assert summary['passed']==0 and summary['stale']==1
