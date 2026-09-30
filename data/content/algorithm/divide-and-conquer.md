---
track: algorithm
difficulty: Hard
algorithms: divide-and-conquer
category: Paradigm
source: authored
io_mode: function
---
# Divide and conquer — Hard — Paradigm

Divide and conquer splits a problem into independent subproblems, solves each recursively, and combines the results. Unlike dynamic programming, the subproblems do not overlap, so no memoisation is needed. For a recurrence T(n) = a·T(n/b) + f(n), with a subproblems of size n/b and combine cost f(n), the master theorem gives:

```latex
T(n)=\begin{cases}\Theta(n^{\log_b a}) & f(n)=O(n^{\log_b a-\epsilon})\\ \Theta(n^{\log_b a}\log n) & f(n)=\Theta(n^{\log_b a})\\ \Theta(f(n)) & f(n)=\Omega(n^{\log_b a+\epsilon})\end{cases}
```

Examples: merge sort (a = 2, b = 2, f = n → O(n log n)), binary search (a = 1, b = 2, f = 1 → O(log n)), fast exponentiation (O(log n)), Karatsuba multiplication (O(n^1.585)), Strassen matrix multiplication (O(n^2.81)), closest pair of points (O(n log n)), and counting inversions during merge sort.

## Strings, math and bit manipulation

Each chunk covers one family of techniques that recur across DSA problems regardless of language.
