#!/usr/bin/env python3
"""Functional correctness check: pull the Python block from each problem,
exec it, and assert against known input/output pairs. This catches logic
bugs that a syntax check misses."""
import re
from pathlib import Path

PROBLEMS = Path(__file__).resolve().parents[1] / "data" / "dsa_problems"
py_re = re.compile(r"### Python\n```python\n(.*?)```", re.DOTALL)


def load(problem_id, func_name):
    text = (PROBLEMS / f"{problem_id}.md").read_text()
    code = py_re.search(text).group(1)
    ns = {}
    exec(code, ns)
    return ns[func_name]


def sorted_lists(x):
    return sorted(sorted(t) for t in x)


CASES = [
    ("two-sum", "two_sum", lambda f: sorted(f([2, 7, 11, 15], 9)) == [0, 1]
        and sorted(f([3, 2, 4], 6)) == [1, 2]),
    ("best-time-to-buy-and-sell-stock", "max_profit",
        lambda f: f([7, 1, 5, 3, 6, 4]) == 5 and f([7, 6, 4, 3, 1]) == 0),
    ("contains-duplicate", "contains_duplicate",
        lambda f: f([1, 2, 3, 1]) is True and f([1, 2, 3, 4]) is False),
    ("product-of-array-except-self", "product_except_self",
        lambda f: f([1, 2, 3, 4]) == [24, 12, 8, 6]),
    ("maximum-subarray", "max_sub_array",
        lambda f: f([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6 and f([-1]) == -1),
    ("maximum-product-subarray", "max_product",
        lambda f: f([2, 3, -2, 4]) == 6 and f([-2, 0, -1]) == 0),
    ("find-minimum-in-rotated-sorted-array", "find_min",
        lambda f: f([3, 4, 5, 1, 2]) == 1 and f([4, 5, 6, 7, 0, 1, 2]) == 0 and f([11]) == 11),
    ("search-in-rotated-sorted-array", "search",
        lambda f: f([4, 5, 6, 7, 0, 1, 2], 0) == 4 and f([4, 5, 6, 7, 0, 1, 2], 3) == -1),
    ("3sum", "three_sum",
        lambda f: sorted_lists(f([-1, 0, 1, 2, -1, -4])) == sorted_lists([[-1, -1, 2], [-1, 0, 1]])),
    ("container-with-most-water", "max_area",
        lambda f: f([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49 and f([1, 1]) == 1),
    ("sum-of-two-integers", "get_sum",
        lambda f: f(1, 2) == 3 and f(-2, 3) == 1 and f(-1, -1) == -2),
    ("number-of-1-bits", "hamming_weight",
        lambda f: f(11) == 3 and f(128) == 1 and f(0) == 0),
    ("counting-bits", "count_bits",
        lambda f: f(5) == [0, 1, 1, 2, 1, 2] and f(2) == [0, 1, 1]),
    ("missing-number", "missing_number",
        lambda f: f([3, 0, 1]) == 2 and f([0, 1]) == 2 and f([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8),
    ("reverse-bits", "reverse_bits",
        lambda f: f(43261596) == 964176192 and f(0) == 0),
    ("climbing-stairs", "climb_stairs",
        lambda f: f(2) == 2 and f(3) == 3 and f(5) == 8),
    ("coin-change", "coin_change",
        lambda f: f([1, 2, 5], 11) == 3 and f([2], 3) == -1 and f([1], 0) == 0),
    ("longest-increasing-subsequence", "length_of_lis",
        lambda f: f([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and f([7, 7, 7, 7]) == 1),
    ("longest-common-subsequence", "longest_common_subsequence",
        lambda f: f("abcde", "ace") == 3 and f("abc", "def") == 0),
    ("word-break", "word_break",
        lambda f: f("leetcode", ["leet", "code"]) is True
        and f("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False),
    ("combination-sum-iv", "combination_sum4",
        lambda f: f([1, 2, 3], 4) == 7 and f([9], 3) == 0),
]


def main():
    passed, failed = 0, []
    for problem_id, func_name, predicate in CASES:
        try:
            f = load(problem_id, func_name)
            if predicate(f):
                passed += 1
            else:
                failed.append((problem_id, "wrong output"))
        except Exception as e:
            failed.append((problem_id, f"{type(e).__name__}: {e}"))
    print(f"Functional tests: {passed}/{len(CASES)} passed")
    for pid, why in failed:
        print(f"  FAIL {pid}: {why}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
