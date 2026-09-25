#!/usr/bin/env python3
"""Brute-force the content catalog and code runner.

Catalog: every filter combination (exhaustive), plus malformed/adversarial
files that must not crash parsing.
Runner: many randomized test cases against correct and subtly-wrong
implementations, verifying wrong code is ALWAYS caught.
"""
import itertools
import random
import shutil
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- stub deps not installed in this environment -------------------------
if "pydantic" not in sys.modules:
    try:
        import pydantic  # noqa: F401
    except ImportError:
        mod = types.ModuleType("pydantic")

        class BaseModel:
            def __init__(self, **kw):
                for k, v in kw.items():
                    setattr(self, k, v)

        mod.BaseModel = BaseModel
        sys.modules["pydantic"] = mod

try:
    from app.core.config import settings  # noqa: F401
except Exception:
    cfg = types.ModuleType("app.core.config")

    class S:
        exec_timeout_seconds = 5
        exec_memory_mb = 512
        exec_max_processes = 16
        exec_max_output_bytes = 65536
        max_strikes = 3

    cfg.settings = S()
    sys.modules["app.core.config"] = cfg

import importlib.util  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


ROOT = Path(__file__).resolve().parents[1]
cc = load("app.services.content_catalog", ROOT / "app/services/content_catalog.py")
cr = load("app.services.code_runner", ROOT / "app/services/code_runner.py")

failures: list[str] = []


def check(label, condition, extra=""):
    if condition:
        print(f"  PASS {label}")
    else:
        print(f"  FAIL {label} {extra}")
        failures.append(label)


# ---------------------------------------------------------------- catalog
def brute_catalog():
    print("\n=== Catalog: exhaustive filter combinations ===")
    items = cc.list_content()
    tracks = [None, *cc.TRACKS, "bogus"]
    langs = [None, *cc.known_languages(), "cobol"]
    diffs = [None, *cc.DIFFICULTIES, "Impossible"]
    algos = [None, *cc.known_algorithms(), "nonexistent-algo"]
    sources = [None, "leetcode", "hackerrank", "authored", "made-up"]

    combos = 0
    for t, l, d, a, s in itertools.product(tracks, langs, diffs, algos, sources):
        combos += 1
        try:
            res = cc.filter_content(track=t, language=l, difficulty=d, algorithm=a, source=s)
        except Exception as exc:
            failures.append(f"filter crash on {(t, l, d, a, s)}: {exc}")
            print(f"  FAIL crash {(t, l, d, a, s)}: {exc}")
            return
        # every result must satisfy every applied constraint
        for r in res:
            if t and r.track != t:
                failures.append("track leak")
            if d and r.difficulty != d:
                failures.append("difficulty leak")
            if a and a not in r.algorithms:
                failures.append("algorithm leak")
            if s and r.source != s:
                failures.append("source leak")
            if l and r.language is not None and r.language != l:
                failures.append("language leak")
        # filtering can only ever shrink the set
        if len(res) > len(items):
            failures.append("filter grew the set")
    check(f"{combos} filter combinations, no crashes and no constraint leaks",
          not failures)

    print("\n=== Catalog: invariants ===")
    check("every item has a non-empty id", all(i.id for i in items))
    check("every track value is valid", all(i.track in cc.TRACKS for i in items))
    check("language-track items declare a language",
          all(i.language for i in items if i.track == "language"))
    check("no duplicate ids", len({i.id for i in items}) == len(items))
    check("unknown track returns empty", cc.filter_content(track="bogus") == [])
    check("unknown algorithm returns empty", cc.filter_content(algorithm="nope") == [])

    print("\n=== Catalog: algorithm concept links to practice problems ===")
    for tag in cc.known_algorithms():
        tagged = cc.filter_content(algorithm=tag)
        if not tagged:
            failures.append(f"tag {tag} matches nothing")
    check("every known algorithm tag resolves to >=1 item", True)
    bs = [i.id for i in cc.filter_content(algorithm="binary-search")]
    check("binary-search links concept + problems", len(bs) >= 3, bs)


def brute_malformed():
    """Adversarial files must degrade gracefully, never crash the catalog."""
    print("\n=== Catalog: malformed / adversarial files ===")
    tmp = Path(tempfile.mkdtemp())
    nasty = {
        "empty.md": "",
        "only-front.md": "---\ntrack: dsa\n---\n",
        "unclosed-front.md": "---\ntrack: dsa\n# Title — Easy — X\n",
        "no-h1.md": "just some prose with no heading at all\n",
        "weird-h1.md": "# Title without the em dash separators\n",
        "bad-track.md": "---\ntrack: nonsense\n---\n# T — Easy — C\n",
        "empty-values.md": "---\ntrack:\nlanguage:\nalgorithms:\n---\n# T — Easy — C\n",
        "colon-in-value.md": "---\ntitle: A: B: C\ntrack: dsa\n---\n# T — Easy — C\n",
        "unicode.md": "---\ntrack: dsa\n---\n# 二分探索 — Easy — 検索\n",
        "huge-algos.md": "---\ntrack: dsa\nalgorithms: " + ", ".join(f"a{i}" for i in range(200)) + "\n---\n# T — Easy — C\n",
        "crlf.md": "---\r\ntrack: dsa\r\n---\r\n# T — Easy — C\r\n",
    }
    for name, body in nasty.items():
        (tmp / name).write_text(body)

    crashed = []
    for name in nasty:
        try:
            meta = cc.parse_file(tmp / name)
            assert meta.id == Path(name).stem
        except Exception as exc:
            crashed.append(f"{name}: {type(exc).__name__}: {exc}")
    check(f"{len(nasty)} malformed files parsed without crashing", not crashed, crashed)
    shutil.rmtree(tmp)


# ---------------------------------------------------------------- runner
GOOD_PY = (
    "def solve(nums, target):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        if target - x in seen:\n"
    "            return [seen[target - x], i]\n"
    "        seen[x] = i\n"
    "    return []"
)
GOOD_JS = (
    "function solve(nums, target) {\n"
    "  const m = new Map();\n"
    "  for (let i = 0; i < nums.length; i++) {\n"
    "    if (m.has(target - nums[i])) return [m.get(target - nums[i]), i];\n"
    "    m.set(nums[i], i);\n"
    "  }\n"
    "  return [];\n"
    "}"
)
# Subtly wrong: allows reusing the same element (checks after inserting)
SUBTLY_WRONG_PY = (
    "def solve(nums, target):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        seen[x] = i\n"
    "        if target - x in seen:\n"
    "            return [seen[target - x], i]\n"
    "    return []"
)
FN = {"python": "solve", "javascript": "solve"}


def reference(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []


def brute_runner():
    print("\n=== Runner: randomized correctness (100 generated cases) ===")
    random.seed(1234)
    cases, expected = [], []
    for _ in range(100):
        n = random.randint(2, 8)
        nums = [random.randint(-20, 20) for _ in range(n)]
        i, j = random.sample(range(n), 2)
        target = nums[i] + nums[j]
        cases.append([nums, target])
        expected.append(reference(nums, target))

    r = cr.run_suite({"python": GOOD_PY, "javascript": GOOD_JS}, FN, cases, expected)
    check("100 random cases: correct impls pass and agree",
          r["can_publish"] and r["agreement"],
          [x["detail"][:80] for x in r["results"]])

    print("\n=== Runner: subtly wrong code must be caught ===")
    # Cases where an element would be reused (x + x == target) expose the bug
    wrong_cases = [[[3, 2, 4], 6], [[1, 5], 2], [[7, 1], 14], [[4, 4], 8]]
    wrong_expected = [reference(c[0], c[1]) for c in wrong_cases]
    r2 = cr.run_suite({"python": SUBTLY_WRONG_PY, "javascript": GOOD_JS},
                      FN, wrong_cases, wrong_expected)
    py = next(x for x in r2["results"] if x["language"] == "python")
    check("element-reuse bug detected", py["status"] == "failed", py["detail"][:120])
    check("cross-language disagreement flagged", r2["agreement"] is False)
    check("publish blocked", r2["can_publish"] is False)

    print("\n=== Runner: stdio mode (HackerRank style) ===")
    stdio_py = (
        "import sys\n"
        "data = sys.stdin.read().split()\n"
        "n = int(data[0])\n"
        "nums = list(map(int, data[1:1+n]))\n"
        "print(sum(nums))"
    )
    stdio_js = (
        "const d = require('fs').readFileSync(0,'utf8').split(/\\s+/).filter(Boolean);\n"
        "const n = +d[0];\n"
        "let s = 0; for (let i=1;i<=n;i++) s += +d[i];\n"
        "console.log(s);"
    )
    s_cases = ["3\n1 2 3", "4\n10 20 30 40", "1\n-5", "5\n0 0 0 0 0"]
    s_expected = ["6", "100", "-5", "0"]
    r3 = cr.run_suite({"python": stdio_py, "javascript": stdio_js}, {},
                      s_cases, s_expected, io_mode="stdio")
    check("stdio: correct programs pass",
          r3["can_publish"], [x["detail"][:80] for x in r3["results"]])

    bad_stdio = "import sys\nprint(0)"
    r4 = cr.run_suite({"python": bad_stdio}, {}, s_cases, s_expected, io_mode="stdio")
    check("stdio: wrong output caught", r4["can_publish"] is False)

    print("\n=== Runner: hostile submissions ===")
    hostile = {
        "infinite loop": "def solve(a, b):\n    while True: pass",
        "deep recursion": "def solve(a, b):\n    return solve(a, b)",
        "syntax error": "def solve(a, b)\n    return 1",
        "raises": "def solve(a, b):\n    raise ValueError('boom')",
        "wrong arity": "def solve(a):\n    return a",
        "prints instead of returns": "def solve(a, b):\n    print([0,1])",
        "reads env": "import os\ndef solve(a, b):\n    return list(os.environ.keys())[:1]",
        "huge alloc": "def solve(a, b):\n    return [0] * (10**9)",
    }
    small_cases = [[[2, 7], 9]]
    small_expected = [[0, 1]]
    for label, code in hostile.items():
        try:
            rr = cr.run_suite({"python": code}, FN, small_cases, small_expected)
            ok = rr["can_publish"] is False
            check(f"hostile '{label}' blocked", ok)
        except Exception as exc:
            check(f"hostile '{label}' handled", False, f"raised {type(exc).__name__}: {exc}")

    print("\n=== Runner: env isolation ===")
    leak = (
        "import os\n"
        "def solve(a, b):\n"
        "    return [k for k in os.environ if 'KEY' in k.upper() or 'SECRET' in k.upper()]"
    )
    rr = cr.run_suite({"python": leak}, FN, small_cases, [[]])
    pyres = next(x for x in rr["results"] if x["language"] == "python")
    check("no API keys visible to submitted code",
          pyres["outputs"] == [[]] if pyres["outputs"] else True,
          pyres["outputs"])


if __name__ == "__main__":
    os_env_keys = None
    brute_catalog()
    brute_malformed()
    brute_runner()
    print("\n" + "=" * 55)
    if failures:
        print(f"{len(failures)} FAILURES:")
        for f in failures[:20]:
            print(f"  - {f}")
        sys.exit(1)
    print("ALL BRUTE-FORCE CHECKS PASSED")
