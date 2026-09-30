---
track: algorithm
difficulty: Medium
algorithms: prefix-sums
category: Algorithm
source: authored
io_mode: function
---
# Prefix sums and difference arrays — Medium — Algorithm

A prefix sum array stores `pre[i]` = sum of the first i elements (with `pre[0] = 0`), so any range sum is `pre[r + 1] - pre[l]` in O(1) after an O(n) build. The 2D version answers rectangle sums in O(1) by inclusion–exclusion. A difference array is the inverse: adding `delta` to every element in \[l, r\] becomes two O(1) writes (`diff[l] += delta`, `diff[r + 1] -= delta`), and one prefix-sum pass rebuilds the final array. Prefix sums combined with a hash map count subarrays with a target sum even when values are negative (see the hash table patterns chunk). Prefix and suffix products solve "product of array except self" without division. Use a Fenwick or segment tree instead when values change between queries.

#### Prefix sums, 2D prefix sums and difference array — Python

```python
from itertools import accumulate

def prefix_sums(nums):
    return [0, *accumulate(nums)]            # pre[i] = sum(nums[:i])

def range_sum(pre, l, r):                     # sum of nums[l..r], inclusive
    return pre[r + 1] - pre[l]

def prefix_2d(grid):
    rows, cols = len(grid), len(grid[0])
    P = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            P[r + 1][c + 1] = grid[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
    return P

def rect_sum(P, r1, c1, r2, c2):              # inclusive corners (r1, c1) to (r2, c2)
    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]

def apply_range_adds(n, updates):             # updates = [(l, r, delta)], inclusive
    diff = [0] * (n + 1)
    for l, r, delta in updates:
        diff[l] += delta
        diff[r + 1] -= delta
    return list(accumulate(diff[:n]))
```
