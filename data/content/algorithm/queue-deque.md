---
track: algorithm
difficulty: Easy
algorithms: queue-deque
category: Data Structure
source: authored
io_mode: function
---
# Queue, deque and circular queue — Easy — Data Structure

A queue is first-in, first-out. Variants: the standard queue; the double-ended queue (deque), which allows O(1) insert and remove at both ends; and the circular queue, a fixed-capacity ring buffer whose head and tail indices wrap around with modulo so no element is ever shifted. Library queues and deques are ring buffers or linked lists underneath. Common patterns: breadth-first search, level-order tree traversal, task scheduling, sliding-window maximum and 0-1 BFS. Removing from the front of a plain dynamic array is O(n) in most languages (Go reslicing and CRuby's `shift` are O(1) exceptions), so use a real queue type.

#### Queue with head index — JavaScript

```javascript
class Queue {
  #items = []; #head = 0;
  push(x) { this.#items.push(x); }
  shift() {
    const x = this.#items[this.#head++];
    if (this.#head > 1024 && this.#head * 2 > this.#items.length) {
      this.#items = this.#items.slice(this.#head); this.#head = 0;
    }
    return x;
  }
  get size() { return this.#items.length - this.#head; }
}
```

#### Circular queue (ring buffer) — C

```c
#define CAP 1024
typedef struct { int buf[CAP]; int head, tail, size; } Queue;

int q_push(Queue *q, int x) {
    if (q->size == CAP) return -1;
    q->buf[q->tail] = x; q->tail = (q->tail + 1) % CAP; q->size++;
    return 0;
}

int q_pop(Queue *q, int *out) {
    if (!q->size) return -1;
    *out = q->buf[q->head]; q->head = (q->head + 1) % CAP; q->size--;
    return 0;
}
```

#### Deque — C#

```csharp
// .NET has no array deque; LinkedList<T> gives O(1) at both ends.
var dq = new LinkedList<int>();
dq.AddLast(1); dq.AddFirst(0);
int front = dq.First!.Value; dq.RemoveFirst();
int back = dq.Last!.Value; dq.RemoveLast();
```
