---
track: algorithm
difficulty: Medium
algorithms: two-pointers
category: Algorithm
source: authored
io_mode: function
---
# Two pointers — Medium — Algorithm

Two indices move through the data according to a rule, replacing a nested loop. Opposite-direction pointers solve pair sum in a sorted array, container with most water, valid palindrome and trapping rain water. Same-direction (fast and slow) pointers solve removing duplicates in place, moving zeros, and linked-list cycle and middle detection. 3-sum sorts the array, fixes one element and runs opposite pointers on the rest.

#### Pair sum in a sorted array — Python

```python
def pair_sum_sorted(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return i, j
        if s < target:
            i += 1
        else:
            j -= 1
    return None
```
