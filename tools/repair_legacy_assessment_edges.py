"""Repair missing edge-category fixtures in legacy coding assessments.

Candidates are generated from the existing argument shapes, then evaluated by
the normal reference runner. Only candidates that produce a complete runner
output are written, with the observed output as the expected value. This keeps
the repair evidence-based instead of guessing expected answers.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "data/curriculum/quiz"
CODE_TYPES = {"fix_bug", "write_snippet"}


def values(item: dict) -> list:
    return [v for test in item.get("tests", []) for v in test.get("args", [])]


def present(item: dict) -> dict[str, bool]:
    vs = values(item)
    return {
        "empty": any(isinstance(v, (list, str, dict)) and len(v) == 0 for v in vs),
        "zero": any(isinstance(v, (int, float)) and not isinstance(v, bool) and v == 0 for v in vs),
        "negative": any(isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0 for v in vs),
        "duplicate": any(isinstance(v, list) and len(v) != len(set(map(repr, v))) for v in vs),
    }


def applicable(item: dict) -> dict[str, bool]:
    vs = values(item)
    return {
        "empty": any(isinstance(v, (list, str, dict)) for v in vs),
        "zero": any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vs),
        "negative": any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vs),
        "duplicate": any(isinstance(v, list) for v in vs),
    }


def candidate(item: dict, category: str) -> list:
    base = [list(t["args"]) for t in item["tests"]]
    # Start from the shortest existing case so optional/shape-specific inputs
    # are not accidentally changed while adding one edge dimension.
    args = list(min(base, key=len))
    if category == "empty":
        for source in base:
            for i, value in enumerate(source):
                if isinstance(value, list): source[i] = [] ; return source
                if isinstance(value, str): source[i] = "" ; return source
                if isinstance(value, dict): source[i] = {} ; return source
    elif category == "duplicate":
        for source in base:
            for i, value in enumerate(source):
                if isinstance(value, list) and value:
                    element = value[0]
                    source[i] = [element, element]
                    return source
    elif category in ("zero", "negative"):
        ranked = sorted(base, key=lambda source: sum(isinstance(v, list) and bool(v) for v in source), reverse=True)
        for source in ranked:
            for i, value in enumerate(source):
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    source[i] = 0 if category == "zero" else (-abs(value) if value else -1)
                    return source
    raise ValueError(f"no candidate shape for {category}")


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from app.services.code_runner import run_suite

    repaired = []
    deferred = []
    requested = set(sys.argv[1:])
    for path in sorted(QUIZ_DIR.glob("*.json")):
        language = path.stem
        if requested and language not in requested:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for item in data.get("items", []):
            if item.get("type") not in CODE_TYPES or not item.get("tests") or not item.get("solution") or not item.get("fn"):
                continue
            have, can = present(item), applicable(item)
            exemptions = item.get("edge_case_exemptions", {})
            if item["id"] in {"cpp-m-tmpl-fix", "java-s06-fix", "cs-s06-fix"}:
                exemptions = item.setdefault("edge_case_exemptions", {})
                before = len(exemptions)
                exemptions.setdefault("empty", "The function contract requires at least one value; empty input would dereference the first element.")
                changed = changed or len(exemptions) != before
            if item["id"] == "py-s06-fix":
                exemptions = item.setdefault("edge_case_exemptions", {})
                before = len(exemptions)
                exemptions.setdefault("negative", "Grid dimensions are non-negative by contract; negative dimensions are invalid input rather than a meaningful execution case.")
                changed = changed or len(exemptions) != before
            if item["id"] == "rs-m-interior-write":
                exemptions = item.setdefault("edge_case_exemptions", {})
                before = len(exemptions)
                exemptions.setdefault("duplicate", "The Rust runner cannot express this Vec<String> return shape; the existing string-list fixtures remain retained as review evidence.")
                changed = changed or len(exemptions) != before
            missing = [k for k in can if can[k] and not have[k] and k not in exemptions]
            if not missing:
                continue
            cases = []
            categories = []
            for category in missing:
                try:
                    cases.append(candidate(item, category)); categories.append(category)
                except ValueError:
                    deferred.append({"id": item["id"], "category": category, "reason": "no compatible argument shape"})
            if not cases:
                continue
            placeholder = item["tests"][0].get("expected")
            report = run_suite({language: item["solution"]}, {language: item["fn"]}, cases, [placeholder] * len(cases))
            result = report["results"][0]
            outputs = result.get("outputs", [])
            if len(outputs) != len(cases):
                for category in categories:
                    deferred.append({"id": item["id"], "category": category, "reason": result.get("detail", "incomplete runner output")})
                continue
            existing_args = {json.dumps(t["args"], sort_keys=True, default=repr) for t in item["tests"]}
            for category, args, expected in zip(categories, cases, outputs):
                key = json.dumps(args, sort_keys=True, default=repr)
                if key not in existing_args:
                    item["tests"].append({"args": args, "expected": expected})
                    existing_args.add(key)
                    repaired.append({"id": item["id"], "category": category})
                    changed = True
        if changed:
            indent = 2 if language == "java" else 1
            path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"repaired": len(repaired), "deferred": len(deferred), "items": repaired, "deferred_items": deferred}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
