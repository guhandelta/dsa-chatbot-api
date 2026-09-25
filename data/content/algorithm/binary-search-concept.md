---
track: algorithm
difficulty: Easy
source: authored
io_mode: function
algorithms: binary-search
---
# Binary Search (concept) — Easy — Searching, Divide & Conquer

## Concept
Binary search repeatedly halves a search space by asking one question whose answer eliminates half the candidates. It needs a *monotonic* space: everything on one side of the answer says "too small", everything on the other says "too big". Sorted arrays are the obvious case, but the technique generalises far beyond them.

## Invariant
Maintain a window `[lo, hi]` guaranteed to contain the answer. Each step compares the midpoint and shrinks the window, never discarding the answer. The loop ends when the window holds exactly one candidate.

## The two shapes
- **Find an exact value:** `while lo <= hi`, return on match, else move past mid.
- **Find a boundary** (first element ≥ target, minimum feasible value): `while lo < hi`, never `mid ± 1` on the side you might keep, and `lo` converges to the answer.

## Thinking Style (transferable pattern)
- The signal is a **sorted input**, or a phrase like "minimise the maximum" / "find the smallest value that works".
- Ask: can I write a predicate `feasible(x)` that is False, False, …, True, True? If yes, binary-search the boundary even when there is no array at all ("binary search on the answer").
- O(log n) in the constraints (n up to 10⁹, or 10⁵ with a log factor budget) is a strong hint.

## Complexity
O(log n) time, O(1) space iteratively; O(log n) stack recursively.

## Common Mistakes
- `(lo + hi) / 2` overflowing in Java/C++ — use `lo + (hi - lo) / 2`.
- Mixing the two loop shapes, causing an infinite loop when `mid == lo`.
- Applying it to unsorted data, or data sorted by the wrong key.

## Practice progression
- **Easy:** `binary-search`, `find-minimum-in-rotated-sorted-array`
- **Medium:** `search-in-rotated-sorted-array`, `longest-increasing-subsequence` (patience + binary search)

## Exercise
Write `first_at_least(nums, target)` returning the index of the first element ≥ target in a sorted array, or `len(nums)` if none qualifies.

### Python
```python
def first_at_least(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

This is the boundary shape: `hi` starts at `len(nums)` (one past the end) so "no such element" falls out naturally, and `hi = mid` never skips a candidate.
