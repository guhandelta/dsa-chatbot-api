---
track: algorithm
difficulty: Easy
algorithms: linked-list
category: Data Structure
source: authored
io_mode: function
---
# Linked list — Easy — Data Structure

A linked list chains nodes by pointers instead of storing them contiguously. Access by position is O(n) and pointer chasing has poor cache locality, so prefer a dynamic array unless you splice nodes you already hold.

| Variant | Links per node | Strength | Typical use |
| --- | --- | --- | --- |
| Singly linked | `next` | O(1) insert and delete at the head | Stacks, adjacency lists, hash chains |
| Doubly linked | `next`, `prev` | O(1) removal of a known node, traversal both ways | LRU caches, deques, browser history |
| Circular | tail's `next` points to the head (singly or doubly) | Any node reaches every node; no null end | Round-robin scheduling, Josephus problem, ring buffers |

When traversing a circular list, stop on returning to the start node rather than on `null`. A dummy (sentinel) head node removes special cases when the head itself may change. Common patterns: fast and slow pointers (Floyd's cycle detection and cycle entry point, middle node, k-th node from the end via a k-step lead), in-place reversal (whole list, sublist, groups of k), and merging sorted lists.

#### Linked list reversal, fast and slow pointers, merge — Python

```python
class Node:
    __slots__ = ("val", "next")
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt

def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def middle(head):                        # second middle when the length is even
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

def cycle_start(head):                   # entry node of a cycle, or None (Floyd)
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:                 # met inside the cycle
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None                          # has_cycle(head) == (cycle_start(head) is not None)

def merge_sorted(a, b):
    dummy = tail = Node(0)               # sentinel avoids a special case for the head
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
```

#### Linked list reverse — Rust

```rust
struct Node { val: i32, next: Option<Box<Node>> }

fn reverse(mut head: Option<Box<Node>>) -> Option<Box<Node>> {
    let mut prev = None;
    while let Some(mut node) = head {
        head = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
```

Rust singly linked lists use `Option<Box<Node>>`; doubly linked lists need `Rc<RefCell<Node>>` with `Weak` back-pointers, or an index-based arena.
