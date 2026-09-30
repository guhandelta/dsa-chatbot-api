---
track: algorithm
difficulty: Medium
algorithms: binary-search-variants
category: Algorithm
source: authored
io_mode: function
---
# Binary search variants and binary search on the answer — Medium — Algorithm

Binary search works on any monotonic predicate, not only sorted arrays: if `feasible(v)` is false up to some point and true after, binary search finds the boundary.

| Problem | Approach |
| --- | --- |
| First and last occurrence | Lower bound of x; upper bound of x minus 1 |
| Search in rotated sorted array | Compare `a[mid]` with `a[hi]` to find the sorted half, then check whether the target lies inside it |
| Find minimum in rotated array | If `a[mid] > a[hi]` go right, else left (including mid) |
| Peak element | If `a[mid] < a[mid + 1]` go right, else left |
| Search a row-major sorted matrix | Treat it as a flat array: row = mid ÷ cols, col = mid mod cols |
| Binary search on the answer | Find the smallest v with `feasible(v)`: ship capacity within D days, Koko eating bananas, split array largest sum, minimum days to make bouquets |
| Real-valued answers | Loop a fixed \~100 iterations instead of comparing with an epsilon |

#### Binary search on the answer — Python

```python
def min_feasible(lo, hi, feasible):    # smallest v in [lo, hi] with feasible(v) true
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

# Example: minimum ship capacity to deliver weights within `days`
def ship_within_days(weights, days):
    def feasible(cap):
        need, load = 1, 0
        for w in weights:
            if load + w > cap:
                need, load = need + 1, 0
            load += w
        return need <= days
    return min_feasible(max(weights), sum(weights), feasible)
```
