"""Validate and summarize the normalized learning-path assessment contract."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.assessment_contract import normalize_item, validate_item

ROOT = Path(__file__).resolve().parents[1]
BANK_DIR = ROOT / "data" / "curriculum" / "quiz"


def audit() -> dict:
    errors: list[str] = []
    counts: dict[str, Counter] = defaultdict(Counter)
    total = 0
    for path in sorted(BANK_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        language = data.get("language", path.stem)
        seen: set[str] = set()
        for raw in data.get("items", []):
            item = normalize_item(raw, language=language)
            total += 1
            if item["id"] in seen:
                errors.append(f"{language}: duplicate id {item['id']}")
            seen.add(item["id"])
            errors.extend(f"{language}/{item.get('id', '<unknown>')}: {e}" for e in validate_item(item))
            counts[language][item["assessment_type"]] += 1
            counts[language]["runtime" if item["runtime_required"] else "non-runtime"] += 1
    return {"status": "pass" if not errors else "fail", "total": total,
            "languages": {k: dict(v) for k, v in sorted(counts.items())}, "errors": errors}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "pass" else 1)
