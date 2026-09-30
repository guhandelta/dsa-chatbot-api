---
track: algorithm
difficulty: Medium
algorithms: floyd-warshall
category: Algorithm
source: authored
io_mode: function
---
# Floyd-Warshall — Medium — Algorithm

Floyd-Warshall computes shortest paths between every pair of vertices by allowing each vertex k in turn as an intermediate: `d[i][j] = min(d[i][j], d[i][k] + d[k][j])`. The k loop must be outermost. A negative value on the diagonal afterwards signals a negative cycle. Replacing min/plus with or/and gives transitive closure (reachability).

#### Floyd-Warshall — Python

```python
def floyd_warshall(d):                  # d = V×V matrix; inf = no edge; 0 on the diagonal
    n = len(d)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == float("inf"):
                continue
            row = d[i]
            for j in range(n):
                if dik + dk[j] < row[j]:
                    row[j] = dik + dk[j]
    return d
```
