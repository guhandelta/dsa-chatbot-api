---
track: algorithm
difficulty: Medium
algorithms: minimum-spanning-tree
category: Algorithm
source: authored
io_mode: function
---
# Minimum spanning tree (Kruskal and Prim) — Medium — Algorithm

A minimum spanning tree connects all vertices of an undirected weighted graph with the least total edge weight. Kruskal sorts edges by weight and adds each edge that joins two different components, tracked with union-find. Prim grows one tree from a start vertex, repeatedly adding the cheapest edge leaving the tree via a min-heap; it suits dense graphs and adjacency lists. Both are greedy and correct by the cut property. Uses: min cost to connect points, network design, clustering.

#### Kruskal's MST — Python

```python
def kruskal(n, edges):                  # edges = [(u, v, w)]
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    total, mst = 0, []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w; mst.append((u, v, w))
    return total, mst                   # len(mst) < n - 1 means the graph is disconnected
```
