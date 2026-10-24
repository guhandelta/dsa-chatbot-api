"""Audit coding-assessment depth without claiming mastery from reference code.

The audit is deliberately conservative: it reports missing evidence categories
as findings, while execution remains the source of truth for correctness.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.assessment_contract import normalize_item

ROOT = Path(__file__).resolve().parents[1]


def _values(item: dict) -> list:
    values = []
    for test in item.get("tests", []):
        values.extend(test.get("args", []))
    return values


def audit() -> dict:
    findings: list[dict] = []
    code_items = 0
    for path in sorted((ROOT / "data/curriculum/quiz").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for raw in data.get("items", []):
            item = normalize_item(raw, language=data.get("language", path.stem))
            if item["assessment_type"] not in ("fix_bug", "write_snippet"):
                continue
            code_items += 1
            tests = item.get("tests", [])
            values = _values(item)
            categories = {
                "empty": any(isinstance(v, (list, str, dict)) and len(v) == 0 for v in values),
                "zero": any(v == 0 for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)),
                "negative": any(v < 0 for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)),
                "duplicate": any(isinstance(v, list) and len(v) != len(set(map(repr, v))) for v in values),
            }
            if len(tests) < 6:
                findings.append({"id": item["id"], "kind": "too_few_tests", "count": len(tests)})
            missing = [name for name, present in categories.items() if not present]
            if missing:
                findings.append({"id": item["id"], "kind": "missing_edge_categories", "categories": missing})
    return {"status": "pass" if not findings else "findings", "code_items": code_items,
            "finding_count": len(findings), "findings": findings}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2))
    raise SystemExit(0)
