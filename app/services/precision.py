"""Precision verification: differential fuzzing + empirical complexity measurement.

The strongest correctness signal available is not an LLM's opinion — it is a
DIFF against a known-correct implementation. Every problem ships a verified
reference solution, so we can generate hundreds of random inputs, run both the
student's code and the reference, and report the exact input where they differ.

That produces feedback like:
    "Your solution returns [0, 0] for nums=[3, 3], target=6. The reference
     returns [0, 1]. You check the map before inserting, so the same element
     is used twice."

instead of:
    "This might have an issue with duplicate values."

The second is a guess. The first is evidence, and it names the input.

Nothing here calls an LLM. Generators are deterministic given a seed, so a
reported counterexample can always be reproduced.
"""
from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, field

from app.services.code_runner import _equal, _run_tier1


# ---------------------------------------------------------------- generators

def _ints(n: int, lo: int = -50, hi: int = 50, rng=random) -> list[int]:
    return [rng.randint(lo, hi) for _ in range(n)]


def _sorted_ints(n: int, rng=random) -> list[int]:
    return sorted(_ints(n, rng=rng))


def _rotated_sorted(n: int, rng=random) -> list[int]:
    base = sorted(set(_ints(max(n, 1), rng=rng)))
    if not base:
        base = [0]
    k = rng.randrange(len(base))
    return base[k:] + base[:k]


def _string(n: int, alphabet: str = "abc", rng=random) -> str:
    return "".join(rng.choice(alphabet) for _ in range(n))


# Per-problem input generators. Each returns one argument list.
# Kept deliberately explicit rather than inferred — a wrong generator produces
# meaningless counterexamples, which is worse than no fuzzing at all.
GENERATORS: dict[str, callable] = {
    "two-sum": lambda rng: (
        lambda nums, i, j: [nums, nums[i] + nums[j]]
    )(_ints(rng.randint(2, 12), rng=rng), 0, 1)
    if True else None,
    "best-time-to-buy-and-sell-stock": lambda rng: [_ints(rng.randint(1, 15), 0, 100, rng)],
    "contains-duplicate": lambda rng: [_ints(rng.randint(1, 15), -8, 8, rng)],
    "product-of-array-except-self": lambda rng: [_ints(rng.randint(2, 8), -6, 6, rng)],
    "maximum-subarray": lambda rng: [_ints(rng.randint(1, 15), rng=rng)],
    "maximum-product-subarray": lambda rng: [_ints(rng.randint(1, 10), -6, 6, rng)],
    "find-minimum-in-rotated-sorted-array": lambda rng: [_rotated_sorted(rng.randint(1, 12), rng)],
    "search-in-rotated-sorted-array": lambda rng: (
        lambda arr: [arr, rng.choice(arr) if rng.random() < 0.7 else rng.randint(-60, 60)]
    )(_rotated_sorted(rng.randint(1, 12), rng)),
    "3sum": lambda rng: [_ints(rng.randint(3, 12), -8, 8, rng)],
    "container-with-most-water": lambda rng: [_ints(rng.randint(2, 15), 0, 30, rng)],
    "sum-of-two-integers": lambda rng: [rng.randint(-500, 500), rng.randint(-500, 500)],
    "number-of-1-bits": lambda rng: [rng.randint(0, 2**32 - 1)],
    "counting-bits": lambda rng: [rng.randint(0, 40)],
    "missing-number": lambda rng: (
        lambda n, miss: [[x for x in range(n + 1) if x != miss]]
    )(rng.randint(1, 15), rng.randint(0, 1)),
    "reverse-bits": lambda rng: [rng.randint(0, 2**32 - 1)],
    "climbing-stairs": lambda rng: [rng.randint(1, 40)],
    "coin-change": lambda rng: [
        sorted({rng.randint(1, 12) for _ in range(rng.randint(1, 4))}),
        rng.randint(0, 60),
    ],
    "longest-increasing-subsequence": lambda rng: [_ints(rng.randint(1, 14), -10, 10, rng)],
    "longest-common-subsequence": lambda rng: [
        _string(rng.randint(0, 10), rng=rng), _string(rng.randint(0, 10), rng=rng)
    ],
    "word-break": lambda rng: [
        _string(rng.randint(1, 10), "ab", rng),
        sorted({_string(rng.randint(1, 3), "ab", rng) for _ in range(rng.randint(1, 5))}),
    ],
    "combination-sum-iv": lambda rng: [
        sorted({rng.randint(1, 6) for _ in range(rng.randint(1, 3))}), rng.randint(0, 15)
    ],
    "binary-search": lambda rng: (
        lambda arr: [arr, rng.choice(arr) if arr and rng.random() < 0.7 else rng.randint(-60, 60)]
    )(sorted(set(_ints(rng.randint(1, 14), rng=rng)))),
}


def _two_sum_gen(rng):
    """Two Sum guarantees exactly one valid answer, so the input must be
    constructed rather than random — otherwise 'no answer exists' cases
    produce spurious diffs."""
    n = rng.randint(2, 12)
    nums = _ints(n, rng=rng)
    i, j = rng.sample(range(n), 2)
    return [nums, nums[i] + nums[j]]


GENERATORS["two-sum"] = _two_sum_gen


# Minimum valid size per list-argument, from each problem's stated
# constraints. Shrinking must not go below these — a counterexample that
# violates the problem's own constraints is not a real bug, and showing one
# to a student is worse than showing nothing.
MIN_LIST_LEN: dict[str, int] = {
    "two-sum": 2,                       # "exactly one solution" needs 2 elements
    "3sum": 3,
    "container-with-most-water": 2,
    "product-of-array-except-self": 2,
    "search-in-rotated-sorted-array": 1,
    "find-minimum-in-rotated-sorted-array": 1,
}


def supports_fuzzing(problem_id: str) -> bool:
    return problem_id in GENERATORS


# ---------------------------------------------------------------- results

@dataclass
class Counterexample:
    args: list
    student_output: object
    reference_output: object

    def describe(self) -> str:
        return (
            f"input {json.dumps(self.args)} → your code returned "
            f"{json.dumps(self.student_output, default=str)}, "
            f"expected {json.dumps(self.reference_output, default=str)}"
        )


@dataclass
class FuzzReport:
    ran: bool = False
    total: int = 0
    passed: int = 0
    counterexamples: list[Counterexample] = field(default_factory=list)
    seed: int = 0
    note: str = ""

    @property
    def all_passed(self) -> bool:
        return self.ran and not self.counterexamples

    def to_dict(self) -> dict:
        return {
            "ran": self.ran,
            "total": self.total,
            "passed": self.passed,
            "seed": self.seed,
            "note": self.note,
            "counterexamples": [
                {
                    "args": c.args,
                    "student_output": c.student_output,
                    "reference_output": c.reference_output,
                    "description": c.describe(),
                }
                for c in self.counterexamples
            ],
        }


def _shrink(args: list, student_code: str, student_fn: str,
            reference_code: str, reference_fn: str, language: str,
            problem_id: str = "") -> list:
    """Shrink a failing input toward a minimal one, so the student sees
    `[3,3], 6` rather than a 12-element array. Only shrinks list arguments,
    and only while the failure still reproduces."""
    min_len = MIN_LIST_LEN.get(problem_id, 1)
    current = list(args)
    improved = True
    while improved:
        improved = False
        for idx, value in enumerate(current):
            if not isinstance(value, list) or len(value) <= min_len:
                continue
            for candidate in (value[: len(value) // 2], value[len(value) // 2:], value[:-1]):
                if len(candidate) < min_len:
                    continue
                trial = list(current)
                trial[idx] = candidate
                try:
                    s = _run_tier1(language, student_code, student_fn, [trial], [None])
                    r = _run_tier1(language, reference_code, reference_fn, [trial], [None])
                except Exception:
                    continue
                if s.status == "failed" and not s.outputs:
                    continue
                if not s.outputs or not r.outputs:
                    continue
                if not _equal(s.outputs[0], r.outputs[0]):
                    current = trial
                    improved = True
                    break
            if improved:
                break
    return current


def differential_fuzz(
    problem_id: str,
    student_code: str,
    student_fn: str,
    reference_code: str,
    reference_fn: str,
    language: str = "python",
    iterations: int = 200,
    seed: int | None = None,
) -> FuzzReport:
    """Run student and reference over many generated inputs and diff them."""
    report = FuzzReport()
    if language not in ("python", "javascript"):
        report.note = f"Fuzzing is only available for Python and JavaScript, not {language}."
        return report
    if not supports_fuzzing(problem_id):
        report.note = "No input generator is defined for this problem."
        return report

    seed = seed if seed is not None else random.randrange(1_000_000)
    report.seed = seed
    rng = random.Random(seed)
    gen = GENERATORS[problem_id]

    cases = []
    for _ in range(iterations):
        try:
            cases.append(gen(rng))
        except Exception:
            continue
    if not cases:
        report.note = "Input generation produced no cases."
        return report

    # One batched process per side rather than one per case — same evidence,
    # a fraction of the process churn.
    student = _run_tier1(language, student_code, student_fn, cases, [None] * len(cases))
    if student.status == "failed" and not student.outputs:
        report.ran = True
        report.total = len(cases)
        report.note = f"Your code errored during fuzzing: {student.detail[:200]}"
        return report

    reference = _run_tier1(language, reference_code, reference_fn, cases, [None] * len(cases))
    if not reference.outputs:
        report.note = "The reference solution could not be executed for this problem."
        return report

    report.ran = True
    report.total = len(cases)

    for args, s_out, r_out in zip(cases, student.outputs, reference.outputs):
        if _equal(s_out, r_out):
            report.passed += 1
        elif len(report.counterexamples) < 3:
            minimal = _shrink(args, student_code, student_fn,
                              reference_code, reference_fn, language,
                              problem_id=problem_id)
            if minimal != args:
                try:
                    s2 = _run_tier1(language, student_code, student_fn, [minimal], [None])
                    r2 = _run_tier1(language, reference_code, reference_fn, [minimal], [None])
                    if s2.outputs and r2.outputs:
                        args, s_out, r_out = minimal, s2.outputs[0], r2.outputs[0]
                except Exception:
                    pass
            report.counterexamples.append(Counterexample(args, s_out, r_out))

    return report


# ---------------------------------------------------------------- complexity

_TIMING_HARNESS_PY = """
import json, sys, time
sys.setrecursionlimit(50000)
{solution}
sizes = json.loads(sys.stdin.read())
out = []
for case in sizes:
    t0 = time.perf_counter()
    {fn}(*case)
    out.append(time.perf_counter() - t0)
print("__T__" + json.dumps(out))
"""


@dataclass
class ComplexityReport:
    ran: bool = False
    sizes: list[int] = field(default_factory=list)
    timings: list[float] = field(default_factory=list)
    estimate: str = ""
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "ran": self.ran, "sizes": self.sizes,
            "timings": [round(t, 6) for t in self.timings],
            "estimate": self.estimate, "note": self.note,
        }


def _classify(sizes: list[int], timings: list[float]) -> str:
    """Fit the growth ratio between successive doublings.

    Deliberately coarse. Wall-clock timing at small n is noisy, so this
    reports a RANGE and is presented to the student as an observation, never
    as a proof. Anything cleverer would be false precision.
    """
    usable = [(n, t) for n, t in zip(sizes, timings) if t > 1e-4]
    if len(usable) < 3:
        return "inconclusive (ran too fast to measure reliably)"

    ratios = []
    for (n1, t1), (n2, t2) in zip(usable, usable[1:]):
        if t1 <= 0 or n1 <= 0:
            continue
        size_ratio = n2 / n1
        time_ratio = t2 / t1
        if size_ratio > 1 and time_ratio > 0:
            # exponent k such that time_ratio ≈ size_ratio ** k
            import math
            ratios.append(math.log(time_ratio) / math.log(size_ratio))
    if not ratios:
        return "inconclusive"

    k = sum(ratios) / len(ratios)
    if k < 0.4:
        return "roughly constant or logarithmic (O(1)–O(log n))"
    if k < 1.35:
        return "roughly linear (O(n) or O(n log n))"
    if k < 2.4:
        return "roughly quadratic (O(n²))"
    return f"worse than quadratic (growth exponent ≈ {k:.1f})"


def measure_complexity(
    student_code: str, student_fn: str, scale_cases: list[list],
    language: str = "python",
) -> ComplexityReport:
    """Time the submission across increasing input sizes and fit the curve."""
    report = ComplexityReport()
    if language != "python":
        report.note = "Complexity measurement currently supports Python only."
        return report
    if len(scale_cases) < 3:
        report.note = "Not enough input sizes to measure growth."
        return report

    import subprocess
    import sys as _sys
    import tempfile
    from pathlib import Path

    harness = _TIMING_HARNESS_PY.format(solution=student_code, fn=student_fn)
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "t.py"
        path.write_text(harness)
        try:
            proc = subprocess.run(
                [_sys.executable, str(path)],
                input=json.dumps(scale_cases),
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            report.note = "Timed out while measuring — likely worse than quadratic."
            return report

    if proc.returncode != 0:
        report.note = f"Could not measure: {proc.stderr.strip()[:200]}"
        return report

    timings = None
    for line in proc.stdout.splitlines():
        if line.startswith("__T__"):
            timings = json.loads(line[5:])
    if not timings:
        report.note = "No timing data produced."
        return report

    sizes = [len(c[0]) if c and isinstance(c[0], list) else c[0] for c in scale_cases]
    report.ran = True
    report.sizes = [int(s) for s in sizes]
    report.timings = timings
    report.estimate = _classify(report.sizes, timings)
    return report


def extract_fn_name(code: str, language: str) -> str | None:
    if language == "python":
        m = re.search(r"^\s*def\s+(\w+)\s*\(", code, re.MULTILINE)
    else:
        m = re.search(r"^\s*function\s+(\w+)\s*\(", code, re.MULTILINE)
    return m.group(1) if m else None
