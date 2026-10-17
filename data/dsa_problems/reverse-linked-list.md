---
track: dsa
difficulty: Easy
source: leetcode
io_mode: linked_list
fn_python: reverse_list
fn_javascript: reverseList
fn_java: reverseList
test_cases: [{"args": [[]], "expected": []}, {"args": [[1]], "expected": [1]}, {"args": [[1, 2]], "expected": [2, 1]}, {"args": [[1, 2, 3, 4, 5]], "expected": [5, 4, 3, 2, 1]}, {"args": [[-3, 0, 2]], "expected": [2, 0, -3]}, {"args": [[2, 2, 2]], "expected": [2, 2, 2]}, {"args": [[0, -1, 0]], "expected": [0, -1, 0]}]
algorithms: linked-list
---
# Reverse Linked List (LC 206) — Easy — Linked List

## Problem
Given the head of a singly linked list, reverse it and return the new head. Test fixtures encode lists as arrays of node values; your function receives `ListNode` objects with `val` and `next` fields. An empty array represents a null head.

## Example
1→2→3→4→5 → 5→4→3→2→1

## Approach
Walk the list keeping prev, curr, next pointers; redirect each node's next to prev. Time O(n), space O(1).

## Hints
- Save curr.next before overwriting it, or you lose the rest of the list.
- Return prev (the old tail), not head.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust uses LeetCode's `Option<Box<ListNode>>`. Node definitions follow LeetCode's.*

### Python
```python
def reverse_list(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev
```

### JavaScript
```javascript
function reverseList(head) {
  let prev = null;
  while (head) {
    const nxt = head.next;
    head.next = prev;
    prev = head;
    head = nxt;
  }
  return prev;
}
```

### Java
```java
public ListNode reverseList(ListNode head) {
    ListNode prev = null;
    while (head != null) {
        ListNode nxt = head.next;
        head.next = prev;
        prev = head;
        head = nxt;
    }
    return prev;
}
```

### C++
```cpp
ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    while (head) {
        ListNode* nxt = head->next;
        head->next = prev;
        prev = head;
        head = nxt;
    }
    return prev;
}
```

### C
```c
struct ListNode* reverseList(struct ListNode* head) {
    struct ListNode* prev = NULL;
    while (head) {
        struct ListNode* nxt = head->next;
        head->next = prev;
        prev = head;
        head = nxt;
    }
    return prev;
}
```

### Rust
```rust
pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
    let mut prev = None;
    let mut cur = head;
    while let Some(mut node) = cur {
        cur = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
```
