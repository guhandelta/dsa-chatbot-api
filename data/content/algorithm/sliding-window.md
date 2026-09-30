---
track: algorithm
difficulty: Medium
algorithms: sliding-window
category: Algorithm
source: authored
io_mode: function
---
# Sliding window — Medium — Algorithm

A sliding window keeps a contiguous range \[left, right\]. The right edge advances every step; the left edge advances while the window violates the constraint. Each index enters and leaves once, so the scan is O(n). Fixed-size windows compute rolling sums or averages; variable windows solve longest substring without repeats, minimum window substring, longest subarray with at most k distinct values, and minimum-size subarray sum. Sliding windows need non-negative values for sum constraints; with negatives, use prefix sums with a hash map.

#### Longest substring without repeating characters — Python

```python
def longest_unique_substring(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```
