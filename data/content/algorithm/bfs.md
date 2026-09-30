---
track: algorithm
difficulty: Medium
algorithms: bfs
category: Algorithm
source: authored
io_mode: function
---
# Breadth-first search (BFS) — Medium — Algorithm

BFS explores vertices in order of distance from the source using a FIFO queue, so the first time a vertex is reached is along a shortest path in an unweighted graph. Mark vertices as visited when they are enqueued, not when dequeued, or they may be enqueued many times. Uses: shortest path in a maze or grid, word ladder, rotting oranges, minimum knight moves, level-order traversal, bipartite checking. Multi-source BFS starts with every source in the queue at distance 0.

#### BFS — Python

```python
from collections import deque

def bfs(adj, src):
    dist = [-1] * len(adj)
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

#### BFS — JavaScript

```javascript
function bfs(adj, src) {
  const dist = new Array(adj.length).fill(-1);
  dist[src] = 0;
  const q = [src];
  for (let head = 0; head < q.length; head++) {      // head index keeps dequeue O(1)
    const u = q[head];
    for (const v of adj[u]) if (dist[v] === -1) { dist[v] = dist[u] + 1; q.push(v); }
  }
  return dist;
}
```

#### BFS — TypeScript

```typescript
function bfs(adj: readonly (readonly number[])[], src: number): number[] {
  const dist: number[] = new Array<number>(adj.length).fill(-1);
  dist[src] = 0;
  const queue: number[] = [src];
  for (let head = 0; head < queue.length; head++) {   // head index keeps dequeue O(1)
    const u = queue[head];
    for (const v of adj[u]) {
      if (dist[v] === -1) {
        dist[v] = dist[u] + 1;
        queue.push(v);
      }
    }
  }
  return dist;
}
```

#### BFS — Java

```java
static int[] bfs(List<List<Integer>> adj, int src) {
    int[] dist = new int[adj.size()];
    Arrays.fill(dist, -1);
    dist[src] = 0;
    ArrayDeque<Integer> q = new ArrayDeque<>();
    q.add(src);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : adj.get(u)) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }
    }
    return dist;
}
```

#### BFS — C#

```csharp
static int[] Bfs(List<int>[] adj, int src) {
    var dist = new int[adj.Length];
    Array.Fill(dist, -1);
    dist[src] = 0;
    var q = new Queue<int>();
    q.Enqueue(src);
    while (q.Count > 0) {
        int u = q.Dequeue();
        foreach (int v in adj[u])
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q.Enqueue(v); }
    }
    return dist;
}
```

#### BFS — C

```c
#include <stdlib.h>

/* Graph in CSR form: neighbours of u are nbr[off[u] .. off[u + 1]) */
void bfs(int n, const int *off, const int *nbr, int src, int *dist) {
    int *q = malloc(n * sizeof *q), head = 0, tail = 0;
    for (int i = 0; i < n; i++) dist[i] = -1;
    dist[src] = 0; q[tail++] = src;
    while (head < tail) {
        int u = q[head++];
        for (int k = off[u]; k < off[u + 1]; k++) {
            int v = nbr[k];
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q[tail++] = v; }
        }
    }
    free(q);
}
```

#### BFS — C++

```cpp
std::vector<int> bfs(const std::vector<std::vector<int>>& adj, int src) {
    std::vector<int> dist(adj.size(), -1);
    dist[src] = 0;
    std::queue<int> q;
    q.push(src);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.push(v); }
    }
    return dist;
}
```

#### BFS — Go

```go
func bfs(adj [][]int, src int) []int {
	dist := make([]int, len(adj))
	for i := range dist {
		dist[i] = -1
	}
	dist[src] = 0
	queue := []int{src}
	for head := 0; head < len(queue); head++ {
		u := queue[head]
		for _, v := range adj[u] {
			if dist[v] == -1 {
				dist[v] = dist[u] + 1
				queue = append(queue, v)
			}
		}
	}
	return dist
}
```

#### BFS — Rust

```rust
use std::collections::VecDeque;

fn bfs(adj: &[Vec<usize>], src: usize) -> Vec<Option<usize>> {
    let mut dist = vec![None; adj.len()];
    dist[src] = Some(0);
    let mut q = VecDeque::from([src]);
    while let Some(u) = q.pop_front() {
        let d = dist[u].unwrap();
        for &v in &adj[u] {
            if dist[v].is_none() { dist[v] = Some(d + 1); q.push_back(v); }
        }
    }
    dist
}
```

#### BFS — Ruby

```ruby
def bfs(adj, src)
  dist = Array.new(adj.size, -1)
  dist[src] = 0
  queue = [src]
  until queue.empty?
    u = queue.shift                     # O(1) amortised in CRuby
    adj[u].each do |v|
      next unless dist[v] == -1
      dist[v] = dist[u] + 1
      queue << v
    end
  end
  dist
end
```
