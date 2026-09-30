---
track: algorithm
difficulty: Easy
algorithms: segment-tree
category: Data Structure
source: authored
io_mode: function
---
# Segment tree — Easy — Data Structure

A segment tree stores an aggregate (sum, min, max, gcd) for every range in a binary partition of the array. Any range query combines O(log n) stored nodes; a point update refreshes one leaf-to-root path. Lazy propagation defers range updates so they also cost O(log n). Choose it over a Fenwick tree when the operation is not invertible (min, max).

#### Iterative segment tree for range sum — Python

```python
class SegTree:                          # 0-indexed, query covers [l, r)
    def __init__(self, arr):
        self.n = len(arr)
        self.t = [0] * self.n + list(arr)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def update(self, i, val):
        i += self.n
        self.t[i] = val
        while i > 1:
            i //= 2
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def query(self, l, r):
        res, l, r = 0, l + self.n, r + self.n
        while l < r:
            if l & 1: res += self.t[l]; l += 1
            if r & 1: r -= 1; res += self.t[r]
            l //= 2; r //= 2
        return res
```
