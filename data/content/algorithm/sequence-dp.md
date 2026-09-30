---
track: algorithm
difficulty: Hard
algorithms: sequence-dp
category: Paradigm
source: authored
io_mode: function
---
# Two-sequence DP: edit distance and longest common subsequence — Hard — Paradigm

`dp[i][j]` answers the question for the first i characters of a and the first j of b. Edit distance takes the diagonal for a match, else 1 plus the minimum of insert, delete and replace. LCS takes the diagonal plus 1 on a match, else the larger of dropping a character from either side. Only the previous row is needed, so space shrinks to one row.

#### Edit distance and LCS — Python

```python
def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = prev[j - 1] if ca == cb else 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[-1]

def lcs_length(a, b):
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0] * (len(b) + 1)
        for j, cb in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]
```
