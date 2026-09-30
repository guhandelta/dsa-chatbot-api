---
track: algorithm
difficulty: Medium
algorithms: topological-sort
category: Algorithm
source: authored
io_mode: function
---
# Topological sort — Medium — Algorithm

A topological order lists every vertex of a directed acyclic graph before all vertices it points to. Kahn's algorithm repeatedly removes vertices with in-degree 0; if fewer than V vertices come out, the graph has a cycle. The DFS alternative appends each vertex after its descendants finish and reverses the result. Uses: course schedule, build order, task dependencies, alien dictionary.

#### Kahn's topological sort — Python

```python
from collections import deque

def topo_sort(n, edges):                # edges = [(u, v)] meaning u before v
    adj, indeg = [[] for _ in range(n)], [0] * n
    for u, v in edges:
        adj[u].append(v); indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None   # None = cycle
```
