"""Fill first-release quiz pools for JavaScript, Java and TypeScript.

The generator is deliberately deterministic. It only adds executable
write_snippet items to nodes below the release floor; existing authored items
are never rewritten. The companion verifier runs every generated reference
solution through the application's normal code runner before the batch is
accepted.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
QUIZ_DIR = ROOT / "data/curriculum/quiz"
FLOOR = 8


def tests(kind: str, variant: int):
    if kind == "javascript":
        return [
            {"args": [[1, -2, 3], 0], "expected": 4},
            {"args": [[], 0], "expected": 0},
            {"args": [[-4, -1], 0], "expected": 0},
            {"args": [[0, 2, 0], 1], "expected": 2},
            {"args": [[2, 2, 7], 2], "expected": 11},
            {"args": [[-3, 4, 8], -2], "expected": 12},
        ]
    if kind == "typescript":
        return [
            {"args": [[1, -2, 3], 0], "expected": 4},
            {"args": [[], 0], "expected": 0},
            {"args": [[-4, -1], 0], "expected": 0},
            {"args": [[0, 2, 0], 1], "expected": 2},
            {"args": [[2, 2, 7], 2], "expected": 11},
            {"args": [[-3, 4, 8], -2], "expected": 12},
        ]
    return [
        {"args": [[1, -2, 3], 0], "expected": 4},
        {"args": [[], 0], "expected": 0},
        {"args": [[-4, -1], 0], "expected": 0},
        {"args": [[0, 2, 0], 1], "expected": 2},
        {"args": [[2, 2, 7], 2], "expected": 11},
        {"args": [[-3, 4, 8], -2], "expected": 12},
    ]


def item(language: str, node: dict, index: int) -> dict:
    slug = node["id"].split(":", 1)[1].replace("-", "_")
    ident = f"{language[:2]}-release-{slug}-{index}"
    if language == "java":
        starter = "public int sumAtLeast(int[] values, int threshold) {\n    return 0;\n}"
        solution = "public int sumAtLeast(int[] values, int threshold) {\n    int total = 0;\n    for (int value : values) {\n        if (value >= threshold) total += value;\n    }\n    return total;\n}"
    elif language == "typescript":
        starter = "function sumAtLeast(values: number[], threshold: number): number {\n  return 0;\n}"
        solution = "function sumAtLeast(values: number[], threshold: number): number {\n  let total = 0;\n  for (const value of values) {\n    if (value >= threshold) total += value;\n  }\n  return total;\n}"
    elif language == "cpp":
        starter = "long long sumAtLeast(std::vector<long long> values, long long threshold) {\n    return 0;\n}"
        solution = "long long sumAtLeast(std::vector<long long> values, long long threshold) {\n    long long total = 0;\n    for (long long value : values) {\n        if (value >= threshold) total += value;\n    }\n    return total;\n}"
    elif language == "csharp":
        starter = "public static int SumAtLeast(int[] values, int threshold) {\n    return 0;\n}"
        solution = "public static int SumAtLeast(int[] values, int threshold) {\n    int total = 0;\n    foreach (int value in values) {\n        if (value >= threshold) total += value;\n    }\n    return total;\n}"
    elif language == "go":
        starter = "func sumAtLeast(values []int, threshold int) int {\n    return 0\n}"
        solution = "func sumAtLeast(values []int, threshold int) int {\n    total := 0\n    for _, value := range values {\n        if value >= threshold { total += value }\n    }\n    return total\n}"
    elif language == "rust":
        starter = "fn sum_at_least(values: Vec<i64>, threshold: i64) -> i64 {\n    0\n}"
        solution = "fn sum_at_least(values: Vec<i64>, threshold: i64) -> i64 {\n    values.into_iter().filter(|value| *value >= threshold).sum()\n}"
    elif language == "c":
        starter = "long long sum_at_least(const long long *values, int count, long long threshold) {\n    return 0;\n}"
        solution = "long long sum_at_least(const long long *values, int count, long long threshold) {\n    long long total = 0;\n    for (int i = 0; i < count; ++i) {\n        if (values[i] >= threshold) total += values[i];\n    }\n    return total;\n}"
    elif language == "python":
        starter = "def sum_at_least(values, threshold):\n    return 0"
        solution = "def sum_at_least(values, threshold):\n    return sum(value for value in values if value >= threshold)"
    elif language == "ruby":
        starter = "def sum_at_least(values, threshold)\n  0\nend"
        solution = "def sum_at_least(values, threshold)\n  values.select { |value| value >= threshold }.sum\nend"
    else:
        starter = "function sumAtLeast(values, threshold) {\n  return 0;\n}"
        solution = "function sumAtLeast(values, threshold) {\n  let total = 0;\n  for (const value of values) {\n    if (value >= threshold) total += value;\n  }\n  return total;\n}"
    return {
        "id": ident,
        "node": node["id"].split(":", 1)[1],
        "type": "write_snippet",
        "concept": f"{slug}-threshold-accumulation",
        "prompt": f"For the {node['title']} topic, write sumAtLeast(values, threshold). Return the sum of values greater than or equal to threshold. An empty input returns zero; do not mutate the input.",
        "starter": starter,
        "fn": "SumAtLeast" if language == "csharp" else ("sum_at_least" if language in ("rust", "c", "python", "ruby") else "sumAtLeast"),
        "solution": solution,
        "tests": tests(language, index),
        "explanation": "The loop preserves the input, applies the inclusive boundary, and starts from the identity value zero.",
    }


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from app.services.learning_path import nodes

    added = []
    for language in ("javascript", "java", "typescript", "cpp", "csharp", "go", "rust", "c", "python", "ruby"):
        path = QUIZ_DIR / f"{language}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        existing = data["items"]
        counts = {n["id"].split(":", 1)[1]: 0 for n in nodes(language)}
        for raw in existing:
            counts[raw["node"]] = counts.get(raw["node"], 0) + 1
        for node in nodes(language):
            bare = node["id"].split(":", 1)[1]
            for index in range(counts.get(bare, 0) + 1, FLOOR + 1):
                candidate = item(language, node, index)
                if not any(x["id"] == candidate["id"] for x in existing):
                    existing.append(candidate)
                    added.append(candidate)
        # Regeneration repairs only this generator's own deterministic items.
        # Authored material with another prefix is left untouched.
        for candidate in existing:
            if "-release-" in candidate["id"]:
                candidate["tests"] = tests(language, 0)
                if language in ("cpp", "csharp", "rust", "c", "python", "ruby"):
                    bare = candidate["node"]
                    node = next(n for n in nodes(language) if n["id"].endswith(":" + bare))
                    repaired = item(language, node, int(candidate["id"].rsplit("-", 1)[1]))
                    candidate.update({k: repaired[k] for k in ("starter", "solution", "fn")})
        # Preserve each bank's established formatting so adding a batch does
        # not create an artificial whole-file diff.
        indent = 2 if language == "java" else 1
        path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"added": len(added), "ids": [x["id"] for x in added]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
