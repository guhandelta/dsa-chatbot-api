---
track: algorithm
difficulty: Medium
algorithms: doubly-linked-list-concept
category: Data Structure
source: authored
io_mode: function
---
# Doubly linked lists — Medium — Data Structure

A doubly linked list stores each value in a node with two links, `prev` and `next`. Because every node knows both neighbours, you can unlink a node you already hold in O(1) and walk the list in either direction. The cost is a second pointer per node and more pointer updates on every change.

## What the structure guarantees
For every node x that is not the head, `x.prev.next == x`. For every node x that is not the tail, `x.next.prev == x`. The head's `prev` and the tail's `next` are null. Any insertion or removal must restore these links on both sides, which is why most bugs come from updating only one of them.

## Operations

| Operation | Cost | Notes |
| --- | --- | --- |
| Unlink or insert next to a node you hold | O(1) | Needs both neighbours, which the node provides |
| Insert or remove at head or tail | O(1) | Requires head and tail pointers |
| Find a value | O(n) | Walk from either end |
| Access by index | O(n) | Walk from the nearer end, at most n/2 steps |
| Traverse forward or backward | O(n) | Backward traversal starts at the tail |
| Extra space | O(n) | Two pointers per node instead of one |

## Removing a node
The same two-case pattern works for any node, including the head, the tail, and a node in the middle:

```
if x.prev != null: x.prev.next = x.next   else: head = x.next
if x.next != null: x.next.prev = x.prev   else: tail = x.prev
```

Save `x.next` before you unlink `x` if you are walking the list while removing from it. A single-node list is the case where both branches run and the list becomes empty.

## Common mistakes
- Updating only one side. Setting `prev.next` without fixing `next.prev` leaves a backward link pointing at a removed node.
- Dereferencing `head.prev` or `tail.next`. Both are null, so removing the head or tail needs the explicit `else` branch.
- Forgetting to move `head` or `tail`. If the removed node was the tail, `tail` must become its predecessor.
- Reading `x.next` after clearing it. Save the successor first.
- Treating the list like a singly linked one by tracking the previous node in a separate variable. The `prev` link already holds it.

## Languages

### Python
Python has no built-in doubly linked list. `collections.deque` is a double-ended queue with O(1) appends and pops at both ends, but it exposes no node handles, so removing an arbitrary node means searching by value in O(n). Write the node class yourself when you need node-level removal.

```python
class DllNode:
    __slots__ = ("val", "prev", "next")

    def __init__(self, val):
        self.val, self.prev, self.next = val, None, None

def unlink(node, head, tail):
    """Remove node from its list; return the new (head, tail)."""
    if node.prev is not None:
        node.prev.next = node.next
    else:
        head = node.next
    if node.next is not None:
        node.next.prev = node.prev
    else:
        tail = node.prev
    node.prev = node.next = None
    return head, tail
```

### JavaScript
JavaScript has no linked-list type in its standard library. `Array.prototype.splice` removes an element in O(n) because it shifts the rest of the array, so use a hand-written node class when you need O(1) unlinking. The pattern is the same as in Python: check each neighbour before updating it.

```javascript
class DllNode {
  constructor(val) {
    this.val = val;
    this.prev = null;
    this.next = null;
  }
}

// Remove node from its list; return the new [head, tail].
function unlink(node, head, tail) {
  if (node.prev !== null) node.prev.next = node.next;
  else head = node.next;
  if (node.next !== null) node.next.prev = node.prev;
  else tail = node.prev;
  node.prev = node.next = null;
  return [head, tail];
}
```

### TypeScript
TypeScript has no built-in doubly linked list either. Declaring `prev` and `next` as `DllNode | null` makes the compiler check that every dereference is guarded, which is exactly the head and tail case from the list above.

```typescript
class DllNode {
  prev: DllNode | null = null;
  next: DllNode | null = null;
  constructor(public val: number) {}
}

function unlink(
  node: DllNode,
  head: DllNode | null,
  tail: DllNode | null,
): [DllNode | null, DllNode | null] {
  if (node.prev !== null) node.prev.next = node.next;
  else head = node.next;
  if (node.next !== null) node.next.prev = node.prev;
  else tail = node.prev;
  node.prev = node.next = null;
  return [head, tail];
}
```

### Java
`java.util.LinkedList` is a doubly linked list, and its Javadoc calls it a doubly-linked list implementation. You do not get node handles, but an iterator stands on a node: `Iterator.remove()` unlinks the element it last returned, so a single pass can delete every match without searching again.

```java
import java.util.*;

LinkedList<Integer> list = new LinkedList<>(List.of(2, 2, 1, 2, 2));
for (Iterator<Integer> it = list.iterator(); it.hasNext(); ) {
    if (it.next() == 2) it.remove();
}
// list is now [1]
```

### C
C has no standard linked-list type. Pass the head and tail by address so the function can update both when it removes an end node. Allocate nodes from one array or individually and free them when the list is no longer needed.

```c
typedef struct DllNode {
    int val;
    struct DllNode *prev, *next;
} DllNode;

/* Unlink node; head and tail are updated through their addresses. */
void unlink_node(DllNode *node, DllNode **head, DllNode **tail) {
    if (node->prev) node->prev->next = node->next;
    else *head = node->next;
    if (node->next) node->next->prev = node->prev;
    else *tail = node->prev;
    node->prev = node->next = NULL;
}
```

### C++
`std::list` is a doubly linked list. `erase` takes an iterator, which identifies a node, and returns the iterator to the element after it, so removing during a forward walk needs no saved pointer. `remove(value)` does the same for every match in one call.

```cpp
#include <list>

std::list<int> xs = {1, 2, 3, 2};
for (auto it = xs.begin(); it != xs.end(); ) {
    if (*it == 2) it = xs.erase(it);
    else ++it;
}
// xs is now {1, 3}
```

### Rust
Rust's `std::collections::LinkedList` is doubly linked, but its documentation recommends `Vec` or `VecDeque` in most cases. Its node-level cursor API is unstable, so stable code cannot unlink a node in place. The usual stable alternative is an index-based arena: store nodes in a `Vec` and keep `prev` and `next` as indices, with a sentinel for "no link".

```rust
const NIL: usize = usize::MAX;

/// Unlink node i; returns the new head index.
fn unlink(i: usize, prev: &mut [usize], next: &mut [usize], head: usize) -> usize {
    let (p, q) = (prev[i], next[i]);
    if p != NIL { next[p] = q; }
    if q != NIL { prev[q] = p; }
    prev[i] = NIL;
    next[i] = NIL;
    if p == NIL { q } else { head }
}
```

### Go
Go's `container/list` package implements a doubly linked list. `Remove` unlinks an element in O(1), and `Next` and `Prev` walk in both directions. Save `e.Next()` before calling `Remove`, because removing `e` clears its links.

```go
import "container/list"

func dllRemoveAll(values []int64, target int64) []int64 {
	l := list.New()
	for _, v := range values {
		l.PushBack(v)
	}
	for e := l.Front(); e != nil; {
		next := e.Next()
		if e.Value.(int64) == target {
			l.Remove(e)
		}
		e = next
	}
	out := []int64{}
	for e := l.Front(); e != nil; e = e.Next() {
		out = append(out, e.Value.(int64))
	}
	return out
}
```

### C#
`System.Collections.Generic.LinkedList<T>` is a doubly linked list. Its nodes are `LinkedListNode<T>` objects with `Previous` and `Next` properties, and `Remove(node)` unlinks a node you hold in O(1). `Find` and `Remove(value)` search first, so they are O(n).

```csharp
public static long[] DllRemoveAll(long[] values, long target)
{
    var list = new LinkedList<long>(values);
    for (var node = list.First; node != null; )
    {
        var next = node.Next;
        if (node.Value == target) list.Remove(node);
        node = next;
    }
    return new List<long>(list).ToArray();
}
```

### Ruby
Ruby has no built-in doubly linked list. `Array#delete` removes every match in O(n) by scanning, so use a `Struct` node when you need node-level unlinking. The `Struct` provides the `prev` and `next` accessors, and the removal logic is the same as in the other languages.

```ruby
DllNode = Struct.new(:val, :prev, :next)

# Unlink node; returns the new [head, tail].
def unlink(node, head, tail)
  if node.prev then node.prev.next = node.next else head = node.next end
  if node.next then node.next.prev = node.prev else tail = node.prev end
  node.prev = node.next = nil
  [head, tail]
end
```
