"""Validate the offline reviewer set without making provider calls."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))

from app.services.content_catalog import SECTIONS, list_content

PATH = ROOT / "data/evals/connected-tutor-pilot.json"


def validate(data: dict) -> int:
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("status") != "review-draft":
        raise ValueError("unsupported evaluation set")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("evaluation cases are required")
    catalog = {item.id: item for item in list_content()}
    seen = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("invalid evaluation case")
        case_id, section, language, focus_id = (case.get(k) for k in ("id", "section", "language", "focus_id"))
        if (not isinstance(case_id, str) or not case_id or case_id in seen
                or not isinstance(section, str) or section not in SECTIONS
                or not isinstance(language, str) or language != "javascript"
                or not isinstance(focus_id, str) or focus_id not in catalog
                or catalog[focus_id].track not in SECTIONS[section]
                or catalog[focus_id].language not in (None, language)):
            raise ValueError("invalid evaluation focus or scope")
        seen.add(case_id)
        if (not isinstance(case.get("question"), str) or not case["question"].strip()
                or any(not isinstance(case.get(key), list) or not case[key]
                       or any(not isinstance(item, str) or not item.strip() for item in case[key])
                       for key in ("review_points", "risks"))):
            raise ValueError("evaluation case needs question and review criteria")
    return len(cases)


if __name__ == "__main__":
    print(f"Validated {validate(json.loads(PATH.read_text(encoding='utf-8')))} draft tutor cases; no provider calls made.")
