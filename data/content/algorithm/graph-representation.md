---
track: algorithm
difficulty: Easy
algorithms: graph-representation
category: Data Structure
source: authored
io_mode: function
---
# Graph representations — Easy — Data Structure

A graph is a set of vertices joined by edges, directed or undirected, weighted or not. Store sparse graphs (E much smaller than V²) as adjacency lists and dense ones as matrices. A grid is an implicit graph whose neighbours are the four offsets `(1,0), (-1,0), (0,1), (0,-1)`.

| Representation | Space | Edge check | Iterate neighbours | Best for |
| --- | --- | --- | --- | --- |
| Adjacency list | O(V + E) | O(degree) | O(degree) | Most real graphs, BFS, DFS, Dijkstra |
| Adjacency matrix | O(V²) | O(1) | O(V) | Dense graphs, Floyd-Warshall |
| Edge list | O(E) | O(E) | O(E) | Kruskal, Bellman-Ford |
| CSR (compressed sparse row) | O(V + E) | O(log degree) if sorted | O(degree), cache-friendly | Large static graphs |

#### Weighted adjacency list — all languages

```text
Python      adj = [[] for _ in range(n)];                       adj[u].append((v, w))
JavaScript  const adj = Array.from({ length: n }, () => []);      adj[u].push([v, w]);
TypeScript  const adj: [number, number][][] = Array.from({ length: n }, () => []);  adj[u].push([v, w]);
Java        List<List<int[]>> adj = new ArrayList<>(); for (int i = 0; i < n; i++) adj.add(new ArrayList<>());  adj.get(u).add(new int[]{v, w});
C#          var adj = new List<(int to, int w)>[n]; for (int i = 0; i < n; i++) adj[i] = new();  adj[u].Add((v, w));
C           struct Edge { int to, w, next; }; int head[N]; /* forward-star: head[] = -1, edges appended to an array */
C++         std::vector<std::vector<std::pair<int, int>>> adj(n);   adj[u].push_back({v, w});
Go          type Edge struct{ to, w int }; adj := make([][]Edge, n);  adj[u] = append(adj[u], Edge{v, w})
Rust        let mut adj: Vec<Vec<(usize, i64)>> = vec![vec![]; n];   adj[u].push((v, w));
Ruby        adj = Array.new(n) { [] };                               adj[u] << [v, w]
```
