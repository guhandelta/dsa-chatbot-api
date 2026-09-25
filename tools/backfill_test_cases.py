#!/usr/bin/env python3
"""Backfill executable test cases into the existing problem files.

No LLM involved. Inputs are hand-authored below (deliberately including edge
cases); EXPECTED values are computed by running the already-verified Python
reference, then independently cross-checked against the JavaScript reference.
A case is only written if both implementations agree — two independently
written solutions agreeing is far stronger evidence than a model's assertion.

Writes `test_cases:` (JSON) and `fn_python` / `fn_javascript` into each file's
front matter, so /analyze can execute a student's submission against them.

    python tools/backfill_test_cases.py           # dry run, prints a report
    python tools/backfill_test_cases.py --write   # write front matter
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "data" / "dsa_problems"

# Hand-authored inputs. Each entry is a list of positional-argument lists.
# Edge cases are deliberate: empty, single element, duplicates, negatives,
# all-same, and boundary values.
INPUTS: dict[str, list[list]] = {
    "two-sum": [
        [[2, 7, 11, 15], 9], [[3, 2, 4], 6], [[3, 3], 6],
        [[-1, -2, -3, -4], -6], [[0, 4, 3, 0], 0], [[1, 2], 3],
    ],
    "best-time-to-buy-and-sell-stock": [
        [[7, 1, 5, 3, 6, 4]], [[7, 6, 4, 3, 1]], [[1]], [[2, 4, 1]],
        [[3, 3, 3]], [[1, 2]],
    ],
    "contains-duplicate": [
        [[1, 2, 3, 1]], [[1, 2, 3, 4]], [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]],
        [[1]], [[-1, -1]], [[0, 1, 2]],
    ],
    "product-of-array-except-self": [
        [[1, 2, 3, 4]], [[-1, 1, 0, -3, 3]], [[2, 3]], [[1, 1, 1]],
        [[5, 0]], [[-1, -2, -3]],
    ],
    "maximum-subarray": [
        [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], [[1]], [[5, 4, -1, 7, 8]],
        [[-1]], [[-2, -1]], [[0, 0, 0]],
    ],
    "maximum-product-subarray": [
        [[2, 3, -2, 4]], [[-2, 0, -1]], [[-2]], [[0, 2]],
        [[-2, 3, -4]], [[3, -1, 4]],
    ],
    "find-minimum-in-rotated-sorted-array": [
        [[3, 4, 5, 1, 2]], [[4, 5, 6, 7, 0, 1, 2]], [[11, 13, 15, 17]],
        [[1]], [[2, 1]], [[5, 1, 2, 3, 4]],
    ],
    "search-in-rotated-sorted-array": [
        [[4, 5, 6, 7, 0, 1, 2], 0], [[4, 5, 6, 7, 0, 1, 2], 3], [[1], 0],
        [[1], 1], [[5, 1, 3], 3], [[1, 3], 3],
    ],
    "3sum": [
        [[-1, 0, 1, 2, -1, -4]], [[0, 1, 1]], [[0, 0, 0]],
        [[-2, 0, 1, 1, 2]], [[1, 2, -2, -1]], [[0, 0, 0, 0]],
    ],
    "container-with-most-water": [
        [[1, 8, 6, 2, 5, 4, 8, 3, 7]], [[1, 1]], [[4, 3, 2, 1, 4]],
        [[1, 2, 1]], [[2, 3, 4, 5, 18, 17, 6]], [[1, 2]],
    ],
    "sum-of-two-integers": [
        [1, 2], [-2, 3], [0, 0], [-1, -1], [5, -5], [1000, 2000],
    ],
    "number-of-1-bits": [
        [11], [128], [0], [4294967293], [1], [255],
    ],
    "counting-bits": [
        [2], [5], [0], [1], [8], [3],
    ],
    "missing-number": [
        [[3, 0, 1]], [[0, 1]], [[9, 6, 4, 2, 3, 5, 7, 0, 1]],
        [[0]], [[1]], [[0, 2]],
    ],
    "reverse-bits": [
        [43261596], [4294967293], [0], [1], [2147483648], [255],
    ],
    "climbing-stairs": [
        [2], [3], [1], [5], [10], [45],
    ],
    "coin-change": [
        [[1, 2, 5], 11], [[2], 3], [[1], 0], [[1], 2],
        [[2, 5, 10, 1], 27], [[186, 419, 83, 408], 6249],
    ],
    "longest-increasing-subsequence": [
        [[10, 9, 2, 5, 3, 7, 101, 18]], [[0, 1, 0, 3, 2, 3]],
        [[7, 7, 7, 7, 7]], [[1]], [[3, 2, 1]], [[1, 2, 3]],
    ],
    "longest-common-subsequence": [
        ["abcde", "ace"], ["abc", "abc"], ["abc", "def"],
        ["", "abc"], ["a", "a"], ["bsbininm", "jmjkbkjkv"],
    ],
    "word-break": [
        ["leetcode", ["leet", "code"]],
        ["applepenapple", ["apple", "pen"]],
        ["catsandog", ["cats", "dog", "sand", "and", "cat"]],
        ["a", ["a"]],
        ["ab", ["a"]],
        ["cars", ["car", "ca", "rs"]],
    ],
    "combination-sum-iv": [
        [[1, 2, 3], 4], [[9], 3], [[1], 1], [[2, 3], 7],
        [[1, 2], 5], [[4, 2, 1], 32],
    ],
    "binary-search": [
        [[-1, 0, 3, 5, 9, 12], 9], [[-1, 0, 3, 5, 9, 12], 2], [[5], 5],
        [[5], -5], [[1, 2], 2], [[1, 2, 3, 4, 5], 1],
    ],
    # reverse-linked-list takes a ListNode, which has no JSON representation —
    # excluded deliberately rather than fudged. Flagged in the report.
    "reverse-linked-list": [],
}

PY_BLOCK = re.compile(r"### Python\n```python\n(.*?)```", re.DOTALL)
JS_BLOCK = re.compile(r"### JavaScript\n```javascript\n(.*?)```", re.DOTALL)
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def py_fn_name(code: str) -> str | None:
    m = re.search(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
    return m.group(1) if m else None


def js_fn_name(code: str) -> str | None:
    m = re.search(r"^function\s+(\w+)\s*\(", code, re.MULTILINE)
    return m.group(1) if m else None


def run_python(code: str, fn: str, cases: list) -> list:
    harness = (
        "import json,sys\n"
        "sys.setrecursionlimit(20000)\n"
        f"{code}\n"
        "cases=json.loads(sys.stdin.read())\n"
        f"print('__R__'+json.dumps([{fn}(*a) for a in cases], default=str))\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.py"
        p.write_text(harness)
        r = subprocess.run([sys.executable, str(p)], input=json.dumps(cases),
                           capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    for line in r.stdout.splitlines():
        if line.startswith("__R__"):
            return json.loads(line[5:])
    raise RuntimeError("no result marker")


def run_js(code: str, fn: str, cases: list) -> list:
    harness = (
        f"{code}\n"
        "const cs=JSON.parse(require('fs').readFileSync(0,'utf8'));\n"
        f"console.log('__R__'+JSON.stringify(cs.map(a=>{fn}(...a))));\n"
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.js"
        p.write_text(harness)
        r = subprocess.run(["node", str(p)], input=json.dumps(cases),
                           capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    for line in r.stdout.splitlines():
        if line.startswith("__R__"):
            return json.loads(line[5:])
    raise RuntimeError("no result marker")


def equal(a, b) -> bool:
    """Order-insensitive for lists of lists (3Sum triplets)."""
    if isinstance(a, list) and isinstance(b, list):
        if a and b and all(isinstance(x, list) for x in a + b):
            return sorted(sorted(x) for x in a) == sorted(sorted(x) for x in b)
    return a == b


def upsert_front_matter(text: str, additions: dict) -> str:
    m = FRONT.match(text)
    lines = [f"{k}: {v}" for k, v in additions.items()]
    if not m:
        return "---\n" + "\n".join(lines) + "\n---\n" + text
    existing = [
        ln for ln in m.group(1).splitlines()
        if ln.split(":", 1)[0].strip() not in additions
    ]
    return "---\n" + "\n".join(existing + lines) + "\n---\n" + text[m.end():]


def main() -> int:
    write = "--write" in sys.argv
    ok = skipped = failed = 0
    report: list[str] = []

    for pid, cases in sorted(INPUTS.items()):
        path = PROBLEMS / f"{pid}.md"
        if not path.is_file():
            report.append(f"  MISSING FILE  {pid}")
            failed += 1
            continue
        if not cases:
            report.append(f"  SKIP (not JSON-expressible)  {pid}")
            skipped += 1
            continue

        text = path.read_text()
        pym, jsm = PY_BLOCK.search(text), JS_BLOCK.search(text)
        if not pym or not jsm:
            report.append(f"  NO REFERENCE  {pid}")
            failed += 1
            continue

        pycode, jscode = pym.group(1), jsm.group(1)
        pyfn, jsfn = py_fn_name(pycode), js_fn_name(jscode)
        if not pyfn or not jsfn:
            report.append(f"  NO FN NAME  {pid}")
            failed += 1
            continue

        try:
            py_out = run_python(pycode, pyfn, cases)
            js_out = run_js(jscode, jsfn, cases)
        except Exception as exc:
            report.append(f"  EXEC FAIL  {pid}: {exc}")
            failed += 1
            continue

        mismatches = [
            f"case {i + 1}: py={p!r} js={j!r}"
            for i, (p, j) in enumerate(zip(py_out, js_out))
            if not equal(p, j)
        ]
        if mismatches:
            report.append(f"  DISAGREEMENT  {pid}: {'; '.join(mismatches[:3])}")
            failed += 1
            continue

        report.append(f"  OK  {pid}: {len(cases)} cases verified by both references")
        ok += 1

        if write:
            payload = [{"args": a, "expected": e} for a, e in zip(cases, py_out)]
            path.write_text(upsert_front_matter(text, {
                "fn_python": pyfn,
                "fn_javascript": jsfn,
                "test_cases": json.dumps(payload),
            }))

    print("\n".join(report))
    print(f"\n{ok} verified, {skipped} skipped, {failed} failed"
          + ("  [WRITTEN]" if write else "  [dry run — pass --write to save]"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
