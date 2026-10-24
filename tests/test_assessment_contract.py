import json
from pathlib import Path

import pytest

from app.services.assessment_contract import normalize_item, spec, validate_item
from tools.audit_assessment_banks import audit


def test_legacy_item_gets_a_stable_contract():
    item = normalize_item({"id": "x", "node": "stage-01", "type": "write_snippet", "concept": "values"}, language="rust")
    assert spec(item).role == "implement"
    assert spec(item).runtime_required and spec(item).hidden_test_required


def test_invalid_metadata_is_reported():
    item = normalize_item({"id": "x", "node": "stage-01", "type": "mcq", "concept": "values"}, language="python")
    item["role"] = "implement"
    assert "role 'implement' does not match 'mcq'" in validate_item(item)
    assert "unknown difficulty 'impossible'" in validate_item({**item, "difficulty": "impossible"})


def test_all_packaged_banks_satisfy_the_contract():
    result = audit()
    assert result["status"] == "pass", result["errors"][:10]
    assert result["total"] > 900
    assert set(result["languages"]) >= {"python", "typescript", "c", "cpp", "rust", "go", "csharp", "ruby"}
