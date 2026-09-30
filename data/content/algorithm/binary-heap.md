---
track: algorithm
difficulty: Easy
algorithms: binary-heap
category: Data Structure
source: authored
io_mode: function
---
# Binary heap and priority queue — Easy — Data Structure

A binary heap is a complete binary tree stored in an array: children of index i are at 2i+1 and 2i+2, its parent at (i−1)/2 rounded down. In a min-heap every parent is ≤ its children. Push appends and sifts up; pop swaps the root with the last element, removes it, and sifts down. Building a heap from n items bottom-up is O(n). Uses: Dijkstra, Prim, task scheduling, and the top K, k-way merge and two-heap patterns covered in the heap patterns chunk.

| Language | Type | Default order | Opposite order |
| --- | --- | --- | --- |
| Python | `heapq` functions on a `list` | Min | Push negated keys or `(-priority, item)` |
| JavaScript | Build | — | Swap the comparator |
| TypeScript | Build a generic `Heap<T>` | — | Swap the comparator |
| Java | `PriorityQueue<T>` | Min | `Comparator.reverseOrder()` |
| C# | `PriorityQueue<TElement, TPriority>` | Min | `Comparer<int>.Create((a, b) => b.CompareTo(a))` |
| C | Build | — | Flip the comparison |
| C++ | `std::priority_queue<T>` | Max | `std::greater<T>` |
| Go | `container/heap` over a type implementing `heap.Interface` | Min when `Less` uses `<` | Make `Less` use `>` |
| Rust | `BinaryHeap<T>` | Max | Wrap in `std::cmp::Reverse` |
| Ruby | Build | — | Swap the comparator block |

#### Binary heap — Python

```python
import heapq

h = []
heapq.heappush(h, (2, "b"))
heapq.heappush(h, (1, "a"))
priority, item = heapq.heappop(h)      # (1, 'a')
heapq.heapify(nums)                    # O(n), in place
top3 = heapq.nlargest(3, nums)         # O(n log k)
```

#### Binary heap — JavaScript

```javascript
class Heap {
  constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
  get size() { return this.a.length; }
  peek() { return this.a[0]; }
  push(x) {
    const a = this.a; a.push(x); let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this.cmp(a[i], a[p]) >= 0) break;
      [a[i], a[p]] = [a[p], a[i]]; i = p;
    }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last; let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1; let m = i;
        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]]; i = m;
      }
    }
    return top;
  }
}
```

#### Binary heap — TypeScript

```typescript
class Heap<T> {
  private readonly a: T[] = [];
  constructor(private readonly cmp: (x: T, y: T) => number) {}

  get size(): number { return this.a.length; }
  peek(): T | undefined { return this.a[0]; }

  push(x: T): void {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this.cmp(a[i], a[p]) >= 0) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }

  pop(): T | undefined {
    const a = this.a;
    if (a.length === 0) return undefined;
    const top = a[0];
    const last = a.pop()!;
    if (a.length > 0) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]];
        i = m;
      }
    }
    return top;
  }
}

const minHeap = new Heap<number>((a, b) => a - b);
const maxHeap = new Heap<[priority: number, id: string]>((x, y) => y[0] - x[0]);
```

#### Binary heap — Java

```java
PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> Integer.compare(x[0], y[0]));
pq.offer(new int[]{2, 7});
int[] top = pq.poll();                 // smallest x[0]
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
```

#### Binary heap — C#

```csharp
var pq = new PriorityQueue<string, int>();   // element, priority
pq.Enqueue("b", 2);
pq.Enqueue("a", 1);
string first = pq.Dequeue();                 // "a"
var maxPq = new PriorityQueue<string, int>(Comparer<int>.Create((a, b) => b.CompareTo(a)));
```

#### Binary heap — C

```c
static void swap_int(int *a, int *b) { int t = *a; *a = *b; *b = t; }

void heap_push(int *h, int *n, int x) {       /* min-heap in h[0..*n) */
    int i = (*n)++; h[i] = x;
    while (i && h[(i - 1) / 2] > h[i]) { swap_int(&h[i], &h[(i - 1) / 2]); i = (i - 1) / 2; }
}

int heap_pop(int *h, int *n) {
    int top = h[0]; h[0] = h[--(*n)]; int i = 0;
    for (;;) {
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < *n && h[l] < h[m]) m = l;
        if (r < *n && h[r] < h[m]) m = r;
        if (m == i) break;
        swap_int(&h[i], &h[m]); i = m;
    }
    return top;
}
```

#### Binary heap — C++

```cpp
std::priority_queue<int> maxh;
maxh.push(5); int m = maxh.top(); maxh.pop();

using P = std::pair<int, int>;
std::priority_queue<P, std::vector<P>, std::greater<P>> minh;   // min-heap of pairs
minh.push({1, 42});
```

#### Binary heap — Go

```go
import "container/heap"

type Item struct {
	prio int
	val  string
}

// MinHeap implements heap.Interface; make Less use > for a max-heap.
type MinHeap []Item

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i].prio < h[j].prio }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x any)        { *h = append(*h, x.(Item)) }
func (h *MinHeap) Pop() any {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

func example() {
	h := &MinHeap{{2, "b"}, {1, "a"}}
	heap.Init(h)                  // O(n)
	heap.Push(h, Item{0, "z"})    // O(log n)
	top := heap.Pop(h).(Item)     // {0 z}
	_ = top
}
```

#### Binary heap — Rust

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

let mut h = BinaryHeap::new();                // max-heap
h.push(Reverse((2, "b")));                    // Reverse turns it into a min-heap
h.push(Reverse((1, "a")));
if let Some(Reverse((priority, item))) = h.pop() { /* (1, "a") */ }
```

#### Binary heap — Ruby

```ruby
class Heap
  def initialize(&cmp)
    @a = []
    @cmp = cmp || ->(x, y) { x <=> y }
  end

  def size = @a.size
  def peek = @a.first

  def push(x)
    @a << x
    i = @a.size - 1
    while i > 0
      p = (i - 1) / 2
      break if @cmp.call(@a[i], @a[p]) >= 0
      @a[i], @a[p] = @a[p], @a[i]
      i = p
    end
    self
  end

  def pop
    return nil if @a.empty?
    top = @a.first
    last = @a.pop
    unless @a.empty?
      @a[0] = last
      i = 0
      loop do
        l, r, m = 2 * i + 1, 2 * i + 2, i
        m = l if l < @a.size && @cmp.call(@a[l], @a[m]) < 0
        m = r if r < @a.size && @cmp.call(@a[r], @a[m]) < 0
        break if m == i
        @a[i], @a[m] = @a[m], @a[i]
        i = m
      end
    end
    top
  end
end

min_heap = Heap.new
max_heap = Heap.new { |x, y| y <=> x }
```
