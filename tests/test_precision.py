# The precision layer: fuzzing must catch real bugs AND must never accuse
# correct code. The second property matters more — a false accusation
# destroys a learner's trust faster than a missed bug.
import re
from pathlib import Path

import pytest

from app.services.precision import (
    MIN_LIST_LEN,
    differential_fuzz,
    extract_fn_name,
    measure_complexity,
    supports_fuzzing,
)

PROBLEMS = Path(__file__).resolve().parents[1] / "data" / "dsa_problems"


def reference(pid: str) -> tuple[str, str]:
    text = (PROBLEMS / f"{pid}.md").read_text()
    code = re.search(r"### Python\n```python\n(.*?)```", text, re.DOTALL).group(1)
    return code, extract_fn_name(code, "python")


BUGGY = {
    "two-sum": "def two_sum(nums,target):\n    seen={}\n    for i,x in enumerate(nums):\n        seen[x]=i\n        if target-x in seen:\n            return [seen[target-x],i]\n    return []",
    "maximum-subarray": "def max_sub_array(nums):\n    best=cur=0\n    for x in nums:\n        cur=max(0,cur+x)\n        best=max(best,cur)\n    return best",
    "binary-search": "def search(nums,target):\n    lo,hi=0,len(nums)-1\n    while lo<hi:\n        mid=(lo+hi)//2\n        if nums[mid]==target: return mid\n        if nums[mid]<target: lo=mid+1\n        else: hi=mid-1\n    return -1",
    "contains-duplicate": "def contains_duplicate(nums):\n    for i in range(1,len(nums)):\n        if nums[i]==nums[i-1]: return True\n    return False",
}

CORRECT = ["two-sum", "maximum-subarray", "binary-search", "contains-duplicate",
           "3sum", "coin-change", "missing-number", "word-break"]


@pytest.mark.parametrize("pid,bad", list(BUGGY.items()))
def test_fuzzing_catches_real_bugs(pid, bad):
    ref_code, ref_fn = reference(pid)
    report = differential_fuzz(
        pid, bad, extract_fn_name(bad, "python"), ref_code, ref_fn,
        "python", iterations=120, seed=7,
    )
    assert report.ran
    assert report.counterexamples, f"{pid}: known bug not detected"
    assert report.counterexamples[0].describe()


@pytest.mark.parametrize("pid", CORRECT)
def test_correct_solutions_never_accused(pid):
    code, fn = reference(pid)
    report = differential_fuzz(pid, code, fn, code, fn, "python",
                               iterations=120, seed=11)
    assert report.ran
    assert not report.counterexamples, f"{pid}: false counterexample"
    assert report.passed == report.total


def test_counterexamples_respect_problem_constraints():
    """A shrunken counterexample must stay within the problem's stated
    constraints — two-sum guarantees at least two elements."""
    ref_code, ref_fn = reference("two-sum")
    report = differential_fuzz(
        "two-sum", BUGGY["two-sum"], "two_sum", ref_code, ref_fn,
        "python", iterations=120, seed=7,
    )
    for c in report.counterexamples:
        assert len(c.args[0]) >= MIN_LIST_LEN["two-sum"]


def test_unsupported_problem_reports_rather_than_guessing():
    report = differential_fuzz("reverse-linked-list", "def f(): pass", "f",
                               "def g(): pass", "g", "python")
    assert not report.ran
    assert report.note


def test_unsupported_language_is_explicit():
    report = differential_fuzz("two-sum", "x", "x", "y", "y", language="rust")
    assert not report.ran
    assert "rust" in report.note.lower()


def test_fuzzing_is_reproducible():
    ref_code, ref_fn = reference("two-sum")
    a = differential_fuzz("two-sum", BUGGY["two-sum"], "two_sum", ref_code,
                          ref_fn, "python", iterations=60, seed=42)
    b = differential_fuzz("two-sum", BUGGY["two-sum"], "two_sum", ref_code,
                          ref_fn, "python", iterations=60, seed=42)
    assert a.passed == b.passed
    assert [c.args for c in a.counterexamples] == [c.args for c in b.counterexamples]


def test_quadratic_is_distinguishable_from_linear():
    quad = "def f(nums):\n    c=0\n    for i in range(len(nums)):\n        for j in range(len(nums)):\n            c+=1\n    return c"
    cases = [[list(range(n))] for n in (200, 400, 800, 1600)]
    report = measure_complexity(quad, "f", cases, "python")
    if report.ran:  # timing can be too fast on a quick machine
        assert "quadratic" in report.estimate or "worse" in report.estimate


def test_supports_fuzzing_flags():
    assert supports_fuzzing("two-sum")
    assert not supports_fuzzing("reverse-linked-list")
