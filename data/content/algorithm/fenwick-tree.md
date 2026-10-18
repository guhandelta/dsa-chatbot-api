---
track: algorithm
difficulty: Hard
algorithms: fenwick-tree
category: Data Structure
source: authored
io_mode: function
---
# Fenwick tree (binary indexed tree) — Hard — Data Structure

A Fenwick tree stores partial sums where index i covers a range of length `i & -i` (its lowest set bit). Updates climb by adding the lowest set bit; prefix queries descend by subtracting it. It is smaller and faster than a segment tree but needs an invertible operation (sum, xor) to answer arbitrary ranges as `prefix(r) - prefix(l - 1)`. Also used to count inversions in O(n log n).

#### Fenwick tree — Python

```python
class Fenwick:                          # public API 0-indexed, internal array 1-indexed
    def __init__(self, n):
        self.t = [0] * (n + 1)

    def add(self, i, delta):
        i += 1
        while i < len(self.t):
            self.t[i] += delta
            i += i & -i

    def prefix(self, i):                # sum of elements [0, i]
        i += 1
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i
        return s
```
