---
track: algorithm
difficulty: Easy
algorithms: union-find
category: Data Structure
source: authored
io_mode: function
---
# Union-find (disjoint set union) — Easy — Data Structure

Union-find tracks which elements belong to the same group under merges. `find` returns a group's representative; `union` links two representatives. Path compression (or path halving) flattens trees during `find`, and union by size attaches the smaller tree under the larger; together they make each operation O(α(n)), where α is the inverse Ackermann function (≤ 4 for any practical n). Uses: Kruskal's MST, cycle detection in undirected graphs, number of connected components, accounts merge, redundant connection.

#### Union-find — Python

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n)); self.sz = [1] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]      # path halving
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.sz[a] < self.sz[b]:
            a, b = b, a
        self.p[b] = a; self.sz[a] += self.sz[b]
        return True
```

#### Union-find — JavaScript

```javascript
class DSU {
  constructor(n) { this.p = Array.from({ length: n }, (_, i) => i); this.sz = new Array(n).fill(1); }
  find(x) { while (this.p[x] !== x) { this.p[x] = this.p[this.p[x]]; x = this.p[x]; } return x; }
  union(a, b) {
    a = this.find(a); b = this.find(b);
    if (a === b) return false;
    if (this.sz[a] < this.sz[b]) [a, b] = [b, a];
    this.p[b] = a; this.sz[a] += this.sz[b];
    return true;
  }
}
```

#### Union-find — TypeScript

```typescript
class DSU {
  private readonly parent: number[];
  private readonly size: number[];

  constructor(n: number) {
    this.parent = Array.from({ length: n }, (_, i) => i);
    this.size = new Array<number>(n).fill(1);
  }

  find(x: number): number {
    while (this.parent[x] !== x) {
      this.parent[x] = this.parent[this.parent[x]];
      x = this.parent[x];
    }
    return x;
  }

  union(a: number, b: number): boolean {
    a = this.find(a);
    b = this.find(b);
    if (a === b) return false;
    if (this.size[a] < this.size[b]) [a, b] = [b, a];
    this.parent[b] = a;
    this.size[a] += this.size[b];
    return true;
  }
}
```

#### Union-find — Java

```java
class DSU {
    private final int[] p, sz;
    DSU(int n) { p = new int[n]; sz = new int[n]; for (int i = 0; i < n; i++) { p[i] = i; sz[i] = 1; } }
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    boolean union(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) { int t = a; a = b; b = t; }
        p[b] = a; sz[a] += sz[b];
        return true;
    }
}
```

#### Union-find — C#

```csharp
class DSU {
    private readonly int[] p, sz;
    public DSU(int n) { p = new int[n]; sz = new int[n]; for (int i = 0; i < n; i++) { p[i] = i; sz[i] = 1; } }
    public int Find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    public bool Union(int a, int b) {
        a = Find(a); b = Find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) (a, b) = (b, a);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
}
```

#### Union-find — C

```c
#include <stdlib.h>

typedef struct { int *p, *sz; } DSU;

DSU dsu_new(int n) {
    DSU d = { malloc(n * sizeof(int)), malloc(n * sizeof(int)) };
    for (int i = 0; i < n; i++) { d.p[i] = i; d.sz[i] = 1; }
    return d;
}
int dsu_find(DSU *d, int x) { while (d->p[x] != x) { d->p[x] = d->p[d->p[x]]; x = d->p[x]; } return x; }
int dsu_union(DSU *d, int a, int b) {
    a = dsu_find(d, a); b = dsu_find(d, b);
    if (a == b) return 0;
    if (d->sz[a] < d->sz[b]) { int t = a; a = b; b = t; }
    d->p[b] = a; d->sz[a] += d->sz[b];
    return 1;
}
void dsu_free(DSU *d) { free(d->p); free(d->sz); }
```

#### Union-find — C++

```cpp
struct DSU {
    std::vector<int> p, sz;
    explicit DSU(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) std::swap(a, b);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};
```

#### Union-find — Go

```go
type DSU struct{ parent, size []int }

func NewDSU(n int) *DSU {
	d := &DSU{parent: make([]int, n), size: make([]int, n)}
	for i := range n {
		d.parent[i], d.size[i] = i, 1
	}
	return d
}

func (d *DSU) Find(x int) int {
	for d.parent[x] != x {
		d.parent[x] = d.parent[d.parent[x]]
		x = d.parent[x]
	}
	return x
}

func (d *DSU) Union(a, b int) bool {
	a, b = d.Find(a), d.Find(b)
	if a == b {
		return false
	}
	if d.size[a] < d.size[b] {
		a, b = b, a
	}
	d.parent[b] = a
	d.size[a] += d.size[b]
	return true
}
```

#### Union-find — Rust

```rust
struct Dsu { p: Vec<usize>, sz: Vec<usize> }

impl Dsu {
    fn new(n: usize) -> Self { Self { p: (0..n).collect(), sz: vec![1; n] } }
    fn find(&mut self, mut x: usize) -> usize {
        while self.p[x] != x { self.p[x] = self.p[self.p[x]]; x = self.p[x]; }
        x
    }
    fn union(&mut self, a: usize, b: usize) -> bool {
        let (mut a, mut b) = (self.find(a), self.find(b));
        if a == b { return false; }
        if self.sz[a] < self.sz[b] { std::mem::swap(&mut a, &mut b); }
        self.p[b] = a; self.sz[a] += self.sz[b];
        true
    }
}
```

#### Union-find — Ruby

```ruby
class DSU
  def initialize(n)
    @p = (0...n).to_a
    @sz = Array.new(n, 1)
  end

  def find(x)
    while @p[x] != x
      @p[x] = @p[@p[x]]
      x = @p[x]
    end
    x
  end

  def union(a, b)
    a, b = find(a), find(b)
    return false if a == b
    a, b = b, a if @sz[a] < @sz[b]
    @p[b] = a
    @sz[a] += @sz[b]
    true
  end
end
```
