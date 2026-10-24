---
track: dsa
difficulty: Easy
source: authored
io_mode: linked_list
fn_python: reverse_list
fn_javascript: reverseList
fn_typescript: reverseList
fn_java: reverseList
fn_cpp: reverse_list
fn_c: reverse_list
fn_rust: reverse_list
fn_go: reverseList
fn_csharp: ReverseList
fn_ruby: reverse_list
test_cases: [{"args": [[]], "expected": []}, {"args": [[7]], "expected": [7]}, {"args": [[8, 9]], "expected": [9, 8]}, {"args": [[1, 2, 3, 4, 5, 6]], "expected": [6, 5, 4, 3, 2, 1]}, {"args": [[-4, 0, 0, 13]], "expected": [13, 0, 0, -4]}, {"args": [[5, 5, 5, 5]], "expected": [5, 5, 5, 5]}, {"args": [[2147483647, -2147483648, 0]], "expected": [0, -2147483648, 2147483647]}, {"args": [[3, 1, 4, 1, 5, 9, 2]], "expected": [2, 9, 5, 1, 4, 1, 3]}]
algorithms: linked-list
---
# Flip a Node Chain — Easy — Linked List

## Problem
You are given the first node of a chain of nodes, where each node holds an integer `val` and a `next` link. The last node's `next` is null. Build a chain that contains the same nodes in the opposite order and return its first node.

Test fixtures describe a chain as an array of values listed from the first node to the last. Your function receives `ListNode` objects with `val` and `next` fields. An empty array means there are no nodes, so the function receives null. Whatever node you return is read from its `next` links, so the returned chain must end at a null link and must contain each node exactly once.

## Example
values 4, 7, 1 → values 1, 7, 4

## Approach
Keep a reference to the flipped part (initially empty) and a reference to the node you are processing. For each node, first remember the rest of the chain, then point the node back at the flipped part, make it the new flipped part, and move on to the remembered rest. When you run out of nodes, the flipped part holds the answer. This visits each node once, so the time is O(n) and the extra space is O(1).

## Hints
- Remember the rest of the chain before you overwrite a node's link, or that rest is lost.
- The first node of the result is the last node you visited, not the original first node.

## Solutions
*Conventions: Java code sits in `class Solution` with `import java.util.*;`. C++ and C assume the `struct ListNode` definition is already in scope. Rust uses `Option<Box<ListNode>>` for links. The linked-list harness executes Python, JavaScript and Java only.*

### Python
```python
def reverse_list(head):
    flipped = None
    node = head
    while node:
        rest = node.next
        node.next = flipped
        flipped = node
        node = rest
    return flipped
```

### JavaScript
```javascript
function reverseList(head) {
  let flipped = null;
  let node = head;
  while (node) {
    const rest = node.next;
    node.next = flipped;
    flipped = node;
    node = rest;
  }
  return flipped;
}
```

### TypeScript
```typescript
function reverseList(head: ListNode | null): ListNode | null {
  let flipped: ListNode | null = null;
  let node = head;
  while (node) {
    const rest: ListNode | null = node.next;
    node.next = flipped;
    flipped = node;
    node = rest;
  }
  return flipped;
}
```

### Java
```java
public ListNode reverseList(ListNode head) {
    ListNode flipped = null;
    ListNode node = head;
    while (node != null) {
        ListNode rest = node.next;
        node.next = flipped;
        flipped = node;
        node = rest;
    }
    return flipped;
}
```

### C++
```cpp
ListNode* reverse_list(ListNode* head) {
    ListNode* flipped = nullptr;
    ListNode* node = head;
    while (node) {
        ListNode* rest = node->next;
        node->next = flipped;
        flipped = node;
        node = rest;
    }
    return flipped;
}
```

### C
```c
struct ListNode* reverse_list(struct ListNode* head) {
    struct ListNode* flipped = NULL;
    struct ListNode* node = head;
    while (node) {
        struct ListNode* rest = node->next;
        node->next = flipped;
        flipped = node;
        node = rest;
    }
    return flipped;
}
```

### Rust
```rust
pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut flipped = None;
    let mut node = head;
    while let Some(mut current) = node {
        node = current.next.take();
        current.next = flipped;
        flipped = Some(current);
    }
    flipped
}
```

### Go
```go
func reverseList(head *ListNode) *ListNode {
	var flipped *ListNode
	node := head
	for node != nil {
		rest := node.Next
		node.Next = flipped
		flipped = node
		node = rest
	}
	return flipped
}
```

### C#
```csharp
public static ListNode? ReverseList(ListNode? head) {
    ListNode? flipped = null;
    ListNode? node = head;
    while (node != null) {
        ListNode? rest = node.next;
        node.next = flipped;
        flipped = node;
        node = rest;
    }
    return flipped;
}
```

### Ruby
```ruby
def reverse_list(head)
  flipped = nil
  node = head
  while node
    rest = node.next
    node.next = flipped
    flipped = node
    node = rest
  end
  flipped
end
```
