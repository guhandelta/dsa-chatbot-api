---
track: algorithm
difficulty: Medium
algorithms: dijkstra
category: Algorithm
source: authored
io_mode: function
---
# Dijkstra's shortest path — Medium — Algorithm

Dijkstra repeatedly takes the unsettled vertex with the smallest tentative distance from a min-heap and relaxes its outgoing edges (if `dist[u] + w < dist[v]`, update `dist[v]` and push it). Instead of a decrease-key operation, push duplicates and skip any popped entry whose distance is stale. It is correct only for non-negative weights; use Bellman-Ford when edges can be negative. Store a `prev[v]` array while relaxing to reconstruct the path. For dense graphs, an O(V²) array scan without a heap is faster. Uses: network delay time, cheapest flights (with a stop-count state), path with minimum effort on a grid.

#### Dijkstra — Python

```python
import heapq

def dijkstra(adj, src):                 # adj[u] = [(v, w), ...]
    dist = [float("inf")] * len(adj)
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                    # stale entry
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist
```

#### Dijkstra — JavaScript

```javascript
// Requires the Heap class from the "Binary heap — JavaScript" chunk.
function dijkstra(adj, src) {               // adj[u] = [[v, w], ...]
  const dist = new Array(adj.length).fill(Infinity);
  dist[src] = 0;
  const pq = new Heap((a, b) => a[0] - b[0]);
  pq.push([0, src]);
  while (pq.size) {
    const [d, u] = pq.pop();
    if (d > dist[u]) continue;
    for (const [v, w] of adj[u]) if (d + w < dist[v]) { dist[v] = d + w; pq.push([dist[v], v]); }
  }
  return dist;
}
```

#### Dijkstra — TypeScript

```typescript
// Requires the Heap<T> class from the "Binary heap — TypeScript" chunk.
type Edge = readonly [to: number, weight: number];

function dijkstra(adj: readonly (readonly Edge[])[], src: number): number[] {
  const dist: number[] = new Array<number>(adj.length).fill(Infinity);
  dist[src] = 0;
  const pq = new Heap<[number, number]>((x, y) => x[0] - y[0]);   // [distance, vertex]
  pq.push([0, src]);
  while (pq.size > 0) {
    const [d, u] = pq.pop()!;
    if (d > dist[u]) continue;                                    // stale entry
    for (const [v, w] of adj[u]) {
      if (d + w < dist[v]) {
        dist[v] = d + w;
        pq.push([dist[v], v]);
      }
    }
  }
  return dist;
}
```

#### Dijkstra — Java

```java
static long[] dijkstra(List<List<int[]>> adj, int src) {   // edge = {v, w}
    long[] dist = new long[adj.size()];
    Arrays.fill(dist, Long.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
    pq.add(new long[]{0, src});
    while (!pq.isEmpty()) {
        long[] top = pq.poll();
        long d = top[0]; int u = (int) top[1];
        if (d > dist[u]) continue;
        for (int[] e : adj.get(u))
            if (d + e[1] < dist[e[0]]) { dist[e[0]] = d + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
    }
    return dist;
}
```

#### Dijkstra — C#

```csharp
static long[] Dijkstra(List<(int to, int w)>[] adj, int src) {
    var dist = new long[adj.Length];
    Array.Fill(dist, long.MaxValue);
    dist[src] = 0;
    var pq = new PriorityQueue<int, long>();
    pq.Enqueue(src, 0);
    while (pq.TryDequeue(out int u, out long d)) {
        if (d > dist[u]) continue;
        foreach (var (v, w) in adj[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.Enqueue(v, dist[v]); }
    }
    return dist;
}
```

#### Dijkstra — C

```c
#include <limits.h>
#include <stdlib.h>

/* Dense O(V^2) version: w[u * n + v] < 0 means no edge. Best when E is close to V^2. */
void dijkstra(int n, const int *w, int src, long long *dist) {
    char *done = calloc(n, 1);
    for (int i = 0; i < n; i++) dist[i] = LLONG_MAX;
    dist[src] = 0;
    for (int it = 0; it < n; it++) {
        int u = -1;
        for (int i = 0; i < n; i++)
            if (!done[i] && (u == -1 || dist[i] < dist[u])) u = i;
        if (dist[u] == LLONG_MAX) break;
        done[u] = 1;
        for (int v = 0; v < n; v++)
            if (w[u * n + v] >= 0 && dist[u] + w[u * n + v] < dist[v]) dist[v] = dist[u] + w[u * n + v];
    }
    free(done);
}
```

#### Dijkstra — C++

```cpp
std::vector<long long> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& adj, int src) {
    std::vector<long long> dist(adj.size(), LLONG_MAX);
    dist[src] = 0;
    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;
    pq.push({0, src});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, w] : adj[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
    }
    return dist;
}
```

#### Dijkstra — Go

```go
import (
	"container/heap"
	"math"
)

type Edge struct{ to, w int }
type entry struct{ d, u int }
type distHeap []entry

func (h distHeap) Len() int           { return len(h) }
func (h distHeap) Less(i, j int) bool { return h[i].d < h[j].d }
func (h distHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *distHeap) Push(x any)        { *h = append(*h, x.(entry)) }
func (h *distHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

func dijkstra(adj [][]Edge, src int) []int {
	dist := make([]int, len(adj))
	for i := range dist {
		dist[i] = math.MaxInt
	}
	dist[src] = 0
	h := &distHeap{{0, src}}                // a one-element slice is already a valid heap
	for h.Len() > 0 {
		cur := heap.Pop(h).(entry)
		if cur.d > dist[cur.u] {
			continue                           // stale entry
		}
		for _, e := range adj[cur.u] {
			if nd := cur.d + e.w; nd < dist[e.to] {
				dist[e.to] = nd
				heap.Push(h, entry{nd, e.to})
			}
		}
	}
	return dist
}
```

#### Dijkstra — Rust

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

fn dijkstra(adj: &[Vec<(usize, u64)>], src: usize) -> Vec<u64> {
    let mut dist = vec![u64::MAX; adj.len()];
    dist[src] = 0;
    let mut pq = BinaryHeap::from([Reverse((0u64, src))]);
    while let Some(Reverse((d, u))) = pq.pop() {
        if d > dist[u] { continue; }
        for &(v, w) in &adj[u] {
            let nd = d + w;
            if nd < dist[v] { dist[v] = nd; pq.push(Reverse((nd, v))); }
        }
    }
    dist
}
```

#### Dijkstra — Ruby

```ruby
# Requires the Heap class from the "Binary heap — Ruby" chunk.
def dijkstra(adj, src)                  # adj[u] = [[v, w], ...]
  dist = Array.new(adj.size, Float::INFINITY)
  dist[src] = 0
  pq = Heap.new { |a, b| a[0] <=> b[0] }
  pq.push([0, src])
  while pq.size > 0
    d, u = pq.pop
    next if d > dist[u]
    adj[u].each do |v, w|
      next unless d + w < dist[v]
      dist[v] = d + w
      pq.push([dist[v], v])
    end
  end
  dist
end
```
