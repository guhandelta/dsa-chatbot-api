---
track: algorithm
difficulty: Medium
algorithms: dfs
category: Algorithm
source: authored
io_mode: function
---
# Depth-first search (DFS) — Medium — Algorithm

DFS follows one path as deep as possible before backtracking, using recursion or an explicit stack. It counts connected components and islands (flood fill), detects cycles (a back edge to a vertex still on the recursion stack in directed graphs, or to a non-parent visited vertex in undirected graphs), produces topological orders, and underlies Tarjan's SCC and bridge algorithms. Prefer the iterative form when depth can exceed the recursion limit.

#### Iterative DFS and island count — Python

```python
def dfs_order(adj, src):
    seen, stack, order = {src}, [src], []
    while stack:
        u = stack.pop()
        order.append(u)
        for v in reversed(adj[u]):
            if v not in seen:
                seen.add(v); stack.append(v)
    return order

def count_islands(grid):                # grid of "1" land and "0" water
    rows, cols, count = len(grid), len(grid[0]), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            count += 1
            stack = [(r, c)]; grid[r][c] = "0"
            while stack:
                i, j = stack.pop()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == "1":
                        grid[ni][nj] = "0"; stack.append((ni, nj))
    return count
```
