---
track: algorithm
difficulty: Medium
algorithms: graph-algorithm-selection
category: Algorithm
source: authored
io_mode: function
---
# Graph algorithm selection guide — Medium — Algorithm

Pick a graph algorithm by the question asked and the edge weights allowed.

| Problem | Algorithm | Time | Constraint |
| --- | --- | --- | --- |
| Shortest path, unweighted | BFS | O(V + E) | — |
| Shortest path, weights 0 or 1 | 0-1 BFS with a deque | O(V + E) | Weights 0 or 1 only |
| Shortest path, non-negative weights | Dijkstra | O((V + E) log V) | No negative edges |
| Shortest path, negative weights | Bellman-Ford (SPFA variant) | O(VE) | Detects negative cycles |
| All-pairs shortest paths | Floyd-Warshall | O(V³) | V up to \~500 |
| Shortest path with a heuristic | A\* | Depends on heuristic | Heuristic must never overestimate |
| Order tasks with dependencies | Topological sort (Kahn or DFS) | O(V + E) | Directed acyclic graph |
| Minimum spanning tree | Kruskal / Prim | O(E log E) / O(E log V) | Undirected, connected |
| Strongly connected components | Tarjan / Kosaraju | O(V + E) | Directed |
| Bridges and articulation points | Tarjan low-link | O(V + E) | Undirected |
| Maximum flow, minimum cut | Edmonds-Karp / Dinic | O(VE²) / O(V²E) | Capacities on edges |
| Two-colouring, bipartite check | BFS or DFS colouring | O(V + E) | — |
