---
track: algorithm
difficulty: Hard
algorithms: longest-increasing-subsequence
category: Paradigm
source: authored
io_mode: function
---
# Longest increasing subsequence — Hard — Paradigm

The O(n²) DP sets `dp[i]` to 1 plus the best `dp[j]` over earlier smaller values. The O(n log n) method keeps `tails[k]`, the smallest possible tail of an increasing subsequence of length k+1; each element replaces the first tail ≥ it (lower bound), or extends the list. The final list length is the LIS length (the list itself is not necessarily a valid subsequence). Use upper bound instead for non-decreasing subsequences.

#### Longest increasing subsequence — Python

```python
from bisect import bisect_left

def lis_length(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```
