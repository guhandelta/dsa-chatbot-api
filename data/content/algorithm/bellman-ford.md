---
track: algorithm
difficulty: Medium
algorithms: bellman-ford
category: Algorithm
source: authored
io_mode: function
---
# Bellman-Ford — Medium — Algorithm

Bellman-Ford relaxes every edge V−1 times; a shortest path has at most V−1 edges, so distances are final afterwards. If any edge still relaxes in one more pass, a negative cycle is reachable. Limiting the passes to k+1 gives shortest paths using at most k+1 edges (cheapest flights within k stops) as long as each pass reads the previous pass's distances.

#### Bellman-Ford — Python

```python
def bellman_ford(n, edges, src):        # edges = [(u, v, w)]
    dist = [float("inf")] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; changed = True
        if not changed:
            break
    if any(dist[u] + w < dist[v] for u, v, w in edges):
        raise ValueError("negative cycle reachable from source")
    return dist
```
