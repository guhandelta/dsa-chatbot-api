"""Add deterministic first-release debugging missions for JS, Java and TS.

These are answer-free learner missions. Their private diagnoses are retained in
the authored source and are stripped by compile_debug_knowledge.py. Every path
node receives two distinct boundary missions so no-repeat pools do not depend
on incidental reference examples.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/curriculum/debug-challenges.json"


def make(language: str, node: dict, index: int) -> dict:
    bare = node["id"].split(":", 1)[1]
    safe = bare.replace("-", "_")
    if language == "java":
        if index == 1:
            code = f"static int sum_{safe}(int[] values) {{ int total = 0; for (int i = 1; i < values.length; i++) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"static int value_{safe}(Integer value) {{ return value == null || value == 0 ? 10 : value; }}"
            failure = "A stored zero is replaced by the fallback."
            diagnosis = "The contract treats zero as a valid value; only null should select the fallback."
        fence = "java"
    elif language == "typescript":
        if index == 1:
            code = f"function sum_{safe}(values: number[]): number {{ let total = 0; for (let i = 1; i < values.length; i++) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"function value_{safe}(value: number | undefined): number {{ return value ? value : 10; }}"
            failure = "A valid zero is treated as absent."
            diagnosis = "Truthiness narrows away zero at runtime; compare explicitly with undefined."
        fence = "typescript"
    elif language == "cpp":
        if index == 1:
            code = f"long long sum_{safe}(const std::vector<long long>& values) {{ long long total = 0; for (size_t i = 1; i < values.size(); ++i) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"int value_{safe}(int value) {{ return value ? value : 10; }}"
            failure = "A valid zero is treated as absent."
            diagnosis = "The contract treats zero as valid; use an explicit missing-value rule."
        fence = "cpp"
    elif language == "csharp":
        if index == 1:
            code = f"static int Sum_{safe}(int[] values) {{ int total = 0; for (int i = 1; i < values.Length; i++) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"static int Value_{safe}(int? value) {{ return value ?? 10; }}"
            failure = "The mission's null/zero contract is not stated at the call site."
            diagnosis = "The nullable value must distinguish null from the valid numeric value zero."
        fence = "csharp"
    elif language == "go":
        if index == 1:
            code = f"func sum_{safe}(values []int) int {{ total := 0; for i := 1; i < len(values); i++ {{ total += values[i] }}; return total }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"func value_{safe}(value int) int {{ if value == 0 {{ return 10 }}; return value }}"
            failure = "A valid zero is treated as absent."
            diagnosis = "The function needs a separate presence signal if zero is a valid stored value."
        fence = "go"
    elif language == "rust":
        if index == 1:
            code = f"fn sum_{safe}(values: &[i64]) -> i64 {{ let mut total = 0; for i in 1..values.len() {{ total += values[i]; }} total }}"
            failure = "The first value is missing from the total."
            diagnosis = "The range starts at one, so the index-zero boundary is skipped."
        else:
            code = f"fn value_{safe}(value: Option<i64>) -> i64 {{ value.unwrap_or(10) }}"
            failure = "The mission's zero-versus-absence contract is not stated."
            diagnosis = "Option distinguishes None from Some(0); the test must preserve zero as a valid value."
        fence = "rust"
    elif language == "c":
        if index == 1:
            code = f"long long sum_{safe}(const long long *values, int count) {{ long long total = 0; for (int i = 1; i < count; ++i) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"int value_{safe}(int value, int present) {{ return value ? value : 10; }}"
            failure = "A present zero is treated as absent."
            diagnosis = "Presence must be checked separately from the numeric value; zero is valid data."
        fence = "c"
    elif language == "python":
        if index == 1:
            code = f"def sum_{safe}(values):\n    total = 0\n    for value in values[1:]:\n        total += value\n    return total"
            failure = "The first value is missing from the total."
            diagnosis = "Slicing from index one silently drops the first element; include the complete input."
        else:
            code = f"def value_{safe}(value):\n    return value or 10"
            failure = "A valid zero is treated as absent."
            diagnosis = "Truthiness conflates zero with absence; use an explicit None check."
        fence = "python"
    elif language == "ruby":
        if index == 1:
            code = f"def sum_{safe}(values)\n  values.drop(1).sum\nend"
            failure = "The first value is missing from the total."
            diagnosis = "drop(1) removes the index-zero boundary before summing."
        else:
            code = f"def value_{safe}(value)\n  value || 10\nend"
            failure = "The missing-value contract is implicit and untested."
            diagnosis = "Ruby treats false and nil as falsey, while zero is truthy; state and test the intended contract explicitly."
        fence = "ruby"
    else:
        if index == 1:
            code = f"function sum_{safe}(values) {{ let total = 0; for (let i = 1; i < values.length; i++) total += values[i]; return total; }}"
            failure = "The first value is missing from the total."
            diagnosis = "The loop starts at one, so the index-zero boundary is skipped."
        else:
            code = f"function value_{safe}(value) {{ return value ? value : 10; }}"
            failure = "A valid zero is treated as absent."
            diagnosis = "Truthiness treats zero as false; the function needs an explicit missing-value contract."
        fence = "javascript"
    return {
        "language": language,
        "subject": language,
        "difficulty": "easy" if index == 1 else "medium",
        "title": f"{node['title']}: boundary mission {index}",
        "code": code,
        "failure": failure,
        "goal": f"Diagnose the {node['title']} failure, state the input boundary that exposes it, and propose a regression test.",
        "node_ids": [node["id"]],
        "private_solution": diagnosis,
        "code_language": language,
        "task_kind": "repair",
    }


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from app.services.learning_path import nodes

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    existing = data["items"]
    fingerprints = {(x["language"], x["subject"], x["code"]) for x in existing}
    added = []
    for language in ("javascript", "java", "typescript", "cpp", "csharp", "go", "rust", "c", "python", "ruby"):
        for node in nodes(language):
            for index in (1, 2):
                candidate = make(language, node, index)
                key = (candidate["language"], candidate["subject"], candidate["code"])
                if key not in fingerprints:
                    existing.append(candidate)
                    fingerprints.add(key)
                    added.append(candidate["title"])
    SOURCE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"added": len(added), "titles": added}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
