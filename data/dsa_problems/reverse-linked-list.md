---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: linked-list
---
# Reverse Linked List (LC 206) — Easy — Linked List

## Problem
Given the head of a singly linked list, reverse it and return the new head.

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
