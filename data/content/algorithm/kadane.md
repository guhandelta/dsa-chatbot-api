---
track: algorithm
difficulty: Hard
algorithms: kadane
category: Paradigm
source: authored
io_mode: function
---
# Kadane's maximum subarray — Hard — Paradigm

Kadane's algorithm tracks the best sum of a subarray ending at the current index: either extend the previous subarray or start fresh at the current element. The global maximum of those values is the answer. For maximum product, track both the maximum and minimum ending here, since a negative number swaps them. For a circular array, the answer is the larger of the normal maximum and total sum minus the minimum subarray (unless all values are negative).

#### Kadane's algorithm — Python

```python
def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```
