---
track: algorithm
difficulty: Medium
algorithms: counting-radix-sort
category: Algorithm
source: authored
io_mode: function
---
# Counting sort and radix sort — Medium — Algorithm

Counting sort tallies how often each key in the range \[0, k\] occurs, then emits keys in order; it is linear when k is O(n). Radix sort (least significant digit first) applies a stable counting pass per digit, so d passes in base b sort fixed-width integers or strings in linear time. Bucket sort distributes uniformly distributed floats into n buckets and sorts each, O(n) on average.

#### Counting sort and radix sort — Python

```python
def counting_sort(a, max_val):          # non-negative integers ≤ max_val
    count = [0] * (max_val + 1)
    for x in a:
        count[x] += 1
    return [v for v, c in enumerate(count) for _ in range(c)]

def radix_sort(a):                      # LSD, base 10, non-negative integers
    exp = 1
    while a and max(a) // exp:
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = [x for b in buckets for x in b]
        exp *= 10
    return a
```
