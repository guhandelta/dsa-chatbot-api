---
track: algorithm
difficulty: Hard
algorithms: backtracking
category: Paradigm
source: authored
io_mode: function
---
# Backtracking — Hard — Paradigm

Backtracking builds a candidate one choice at a time, recurses, then undoes the choice before trying the next. Pruning cuts branches that cannot lead to a valid answer (a running sum over target, a queen under attack). Template: if the candidate is complete, record a copy; otherwise, for each valid choice, choose, recurse, un-choose. To skip duplicate results from repeated values, sort first and skip a value equal to its predecessor at the same depth. Problems: subsets, permutations, combinations, combination sum, N-Queens, Sudoku solver, word search, palindrome partitioning, generate parentheses.

#### Subsets, permutations and N-Queens — Python

```python
def subsets(nums):
    res, path = [], []
    def go(start):
        res.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return res

def permutations(nums):
    res, path, used = [], [], [False] * len(nums)
    def go():
        if len(path) == len(nums):
            res.append(path[:]); return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True; path.append(x)
            go()
            path.pop(); used[i] = False
    go()
    return res

def n_queens(n):
    cols, diag1, diag2, board, res = set(), set(), set(), [], []
    def place(r):
        if r == n:
            res.append(["." * c + "Q" + "." * (n - c - 1) for c in board]); return
        for c in range(n):
            if c in cols or r - c in diag1 or r + c in diag2:
                continue
            cols.add(c); diag1.add(r - c); diag2.add(r + c); board.append(c)
            place(r + 1)
            cols.remove(c); diag1.remove(r - c); diag2.remove(r + c); board.pop()
    place(0)
    return res
```
