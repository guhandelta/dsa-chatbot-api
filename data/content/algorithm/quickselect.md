---
track: algorithm
difficulty: Medium
algorithms: quickselect
category: Algorithm
source: authored
io_mode: function
---
# Quickselect (k-th smallest element) — Medium — Algorithm

Quickselect partitions like quicksort but continues into only the side that contains index k, so the expected work is n + n/2 + n/4 + … = O(n). Library versions: C++ `std::nth_element`, Rust `select_nth_unstable`. A size-k heap (O(n log k)) is the alternative when data streams in. Median of medians guarantees O(n) worst case but is slower in practice.

#### Quickselect — Python

```python
import random

def quickselect(a, k):                  # k-th smallest, 0-indexed; mutates a
    lo, hi = 0, len(a) - 1
    while True:
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]; i += 1
        a[i], a[hi] = a[hi], a[i]
        if i == k:
            return a[i]
        if i < k:
            lo = i + 1
        else:
            hi = i - 1
```
