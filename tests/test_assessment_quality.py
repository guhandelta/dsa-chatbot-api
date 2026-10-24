from tools.audit_assessment_quality import audit


def test_coding_assessment_quality_audit_runs_and_has_reference_scope():
    result = audit()
    assert result["code_items"] > 200
    assert result["finding_count"] < result["code_items"]
    assert all(f["id"] and f["kind"] for f in result["findings"])
