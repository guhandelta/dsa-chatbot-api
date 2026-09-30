---
track: algorithm
difficulty: Medium
algorithms: strongly-connected-components
category: Algorithm
source: authored
io_mode: function
---
# Strongly connected components (Tarjan) — Medium — Algorithm

A strongly connected component is a maximal set of vertices where each can reach every other. Tarjan's algorithm runs one DFS, giving each vertex a discovery index and a low-link value (the smallest index reachable through its subtree and one back edge); when a vertex's low-link equals its own index, it roots a component, which is popped from the stack. Kosaraju's alternative runs DFS twice, once on the reversed graph. Condensing SCCs yields a DAG. The same low-link idea finds bridges and articulation points in undirected graphs.

#### Tarjan's SCC — Python

```python
import sys

def tarjan_scc(adj):
    sys.setrecursionlimit(max(10_000, 2 * len(adj) + 10))
    n, counter = len(adj), [0]
    index, low = [-1] * n, [0] * n
    on_stack, stack, comps = [False] * n, [], []

    def strong(u):
        index[u] = low[u] = counter[0]; counter[0] += 1
        stack.append(u); on_stack[u] = True
        for v in adj[u]:
            if index[v] == -1:
                strong(v); low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], index[v])
        if low[u] == index[u]:
            comp = []
            while True:
                w = stack.pop(); on_stack[w] = False; comp.append(w)
                if w == u:
                    break
            comps.append(comp)

    for u in range(n):
        if index[u] == -1:
            strong(u)
    return comps
```

## Algorithm paradigms

Each chunk covers one problem-solving strategy: when it applies, how to structure it, and the classic problems it solves.
