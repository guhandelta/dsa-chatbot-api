---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: doubly-linked-list
fn_python: dll_remove_all
fn_javascript: dllRemoveAll
fn_typescript: dllRemoveAll
fn_java: dllRemoveAll
fn_cpp: dll_remove_all
fn_c: dll_remove_all
fn_rust: dll_remove_all
fn_go: dllRemoveAll
fn_csharp: DllRemoveAll
fn_ruby: dll_remove_all
test_cases: [{"args": [[], 3], "expected": []}, {"args": [[7], 7], "expected": []}, {"args": [[7], 4], "expected": [7]}, {"args": [[1, 2, 3, 4, 5], 3], "expected": [1, 2, 4, 5]}, {"args": [[2, 2, 1, 2, 2], 2], "expected": [1]}, {"args": [[1, 2, 3], 1], "expected": [2, 3]}, {"args": [[1, 2, 3], 3], "expected": [1, 2]}, {"args": [[4, 4, 4], 4], "expected": []}, {"args": [[1, 2, 1, 3, 1], 1], "expected": [2, 3]}, {"args": [[5, 6, 7], 9], "expected": [5, 6, 7]}, {"args": [[-3, 0, -3, 8], -3], "expected": [0, 8]}]
---
# Remove All From a Doubly Linked List — Medium — Data Structure

## Problem
Given an integer array `values` and an integer `target`, build a doubly linked list in which the node at index i holds `values[i]`. Each node has a `prev` and a `next` link; the head's `prev` and the tail's `next` are null. Then remove every node whose value equals `target` by relinking its neighbours: if the removed node is the head, the next node becomes the head, and if it is the tail, the previous node becomes the tail. Return the values of the surviving nodes from head to tail as an array.

The node type is internal to your solution; the function receives and returns only `int[]` and an integer. An empty input, or a list where every node is removed, returns an empty array. Duplicates of `target` are all removed.

## Example
values = [1,2,3,4,5], target = 3 → [1,2,4,5]
values = [2,2,1,2,2], target = 2 → [1] (both the head and the tail are removed, one node at a time)

## Approach
Build the list in one pass, keeping a tail pointer. Then walk the list once. Save `next` before touching a node, since unlinking overwrites the links. For each match, set the predecessor's `next` (or move `head` if there is no predecessor) and the successor's `prev` (or move `tail` if there is no successor). Finally walk from the head to collect the values. Time O(n), space O(n) for the nodes and the output.

## Hints
- Save the node's `next` before you unlink it; the unlink overwrites it.
- Two cases need special handling: a removed head has no `prev` to update, and a removed tail has no `next`.
- Removing a node does not change its neighbours' values, so checking each node in order is enough. Removing several nodes in a row (e.g. `[4,4,4]`) works the same way, one at a time.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in a class with `import java.util.*;`. The node types are defined in the same block as each function.*

### Python
```python
class DllNode:
    __slots__ = ("val", "prev", "next")

    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None

def dll_remove_all(values, target):
    head = tail = None
    for v in values:
        node = DllNode(v)
        if tail is None:
            head = node
        else:
            tail.next = node
            node.prev = tail
        tail = node

    node = head
    while node is not None:
        nxt = node.next
        if node.val == target:
            if node.prev is not None:
                node.prev.next = node.next
            else:
                head = node.next
            if node.next is not None:
                node.next.prev = node.prev
            else:
                tail = node.prev
            node.prev = node.next = None
        node = nxt

    out = []
    node = head
    while node is not None:
        out.append(node.val)
        node = node.next
    return out
```

### JavaScript
```javascript
class DllNode {
  constructor(val) {
    this.val = val;
    this.prev = null;
    this.next = null;
  }
}

function dllRemoveAll(values, target) {
  let head = null, tail = null;
  for (const v of values) {
    const node = new DllNode(v);
    if (tail === null) head = node;
    else { tail.next = node; node.prev = tail; }
    tail = node;
  }

  let node = head;
  while (node !== null) {
    const nxt = node.next;
    if (node.val === target) {
      if (node.prev !== null) node.prev.next = node.next;
      else head = node.next;
      if (node.next !== null) node.next.prev = node.prev;
      else tail = node.prev;
      node.prev = node.next = null;
    }
    node = nxt;
  }

  const out = [];
  for (node = head; node !== null; node = node.next) out.push(node.val);
  return out;
}
```

### TypeScript
```typescript
class DllNode {
  val: number;
  prev: DllNode | null = null;
  next: DllNode | null = null;
  constructor(val: number) {
    this.val = val;
  }
}

function dllRemoveAll(values: number[], target: number): number[] {
  let head: DllNode | null = null, tail: DllNode | null = null;
  for (const v of values) {
    const node = new DllNode(v);
    if (tail === null) head = node;
    else { tail.next = node; node.prev = tail; }
    tail = node;
  }

  let node = head;
  while (node !== null) {
    const nxt: DllNode | null = node.next;
    if (node.val === target) {
      if (node.prev !== null) node.prev.next = node.next;
      else head = node.next;
      if (node.next !== null) node.next.prev = node.prev;
      else tail = node.prev;
      node.prev = node.next = null;
    }
    node = nxt;
  }

  const out: number[] = [];
  for (node = head; node !== null; node = node.next) out.push(node.val);
  return out;
}
```

### Java
```java
static class DllNode {
    long val;
    DllNode prev, next;
    DllNode(long val) { this.val = val; }
}

public long[] dllRemoveAll(long[] values, long target) {
    DllNode head = null, tail = null;
    for (long v : values) {
        DllNode node = new DllNode(v);
        if (tail == null) head = node;
        else { tail.next = node; node.prev = tail; }
        tail = node;
    }

    DllNode node = head;
    while (node != null) {
        DllNode nxt = node.next;
        if (node.val == target) {
            if (node.prev != null) node.prev.next = node.next;
            else head = node.next;
            if (node.next != null) node.next.prev = node.prev;
            else tail = node.prev;
            node.prev = node.next = null;
        }
        node = nxt;
    }

    int count = 0;
    for (node = head; node != null; node = node.next) count++;
    long[] out = new long[count];
    int k = 0;
    for (node = head; node != null; node = node.next) out[k++] = node.val;
    return out;
}
```

### C++
```cpp
struct DllNode {
    long long val;
    DllNode* prev;
    DllNode* next;
    explicit DllNode(long long v) : val(v), prev(nullptr), next(nullptr) {}
};

std::vector<long long> dll_remove_all(std::vector<long long>& values, long long target) {
    // Reserve up front so node addresses stay stable while linking.
    std::vector<DllNode> pool;
    pool.reserve(values.size());
    DllNode* head = nullptr;
    DllNode* tail = nullptr;
    for (long long v : values) {
        pool.emplace_back(v);
        DllNode* node = &pool.back();
        if (tail == nullptr) head = node;
        else { tail->next = node; node->prev = tail; }
        tail = node;
    }

    for (DllNode* node = head; node != nullptr;) {
        DllNode* nxt = node->next;
        if (node->val == target) {
            if (node->prev != nullptr) node->prev->next = node->next;
            else head = node->next;
            if (node->next != nullptr) node->next->prev = node->prev;
            else tail = node->prev;
            node->prev = node->next = nullptr;
        }
        node = nxt;
    }

    std::vector<long long> out;
    for (DllNode* node = head; node != nullptr; node = node->next) out.push_back(node->val);
    return out;
}
```

### C
```c
typedef struct DllNode {
    long long val;
    struct DllNode* prev;
    struct DllNode* next;
} DllNode;

long long* dll_remove_all(long long* values, int valuesSize, long long target, int* returnSize) {
    int cap = valuesSize > 0 ? valuesSize : 1;
    DllNode* pool = malloc(sizeof(DllNode) * cap);
    long long* out = malloc(sizeof(long long) * cap);
    DllNode* head = NULL;
    DllNode* tail = NULL;
    for (int i = 0; i < valuesSize; i++) {
        DllNode* node = &pool[i];
        node->val = values[i];
        node->prev = tail;
        node->next = NULL;
        if (tail == NULL) head = node;
        else tail->next = node;
        tail = node;
    }

    for (DllNode* node = head; node != NULL;) {
        DllNode* nxt = node->next;
        if (node->val == target) {
            if (node->prev != NULL) node->prev->next = node->next;
            else head = node->next;
            if (node->next != NULL) node->next->prev = node->prev;
            else tail = node->prev;
            node->prev = node->next = NULL;
        }
        node = nxt;
    }

    int k = 0;
    for (DllNode* node = head; node != NULL; node = node->next) out[k++] = node->val;
    *returnSize = k;
    free(pool);
    return out;
}
```

### Rust
```rust
pub fn dll_remove_all(values: Vec<i64>, target: i64) -> Vec<i64> {
    // Index-based arena: prev/next hold node indices, NIL means no link.
    const NIL: usize = usize::MAX;
    let n = values.len();
    let mut prev = vec![NIL; n];
    let mut next = vec![NIL; n];
    for i in 1..n {
        prev[i] = i - 1;
        next[i - 1] = i;
    }
    let mut head = if n > 0 { 0 } else { NIL };

    for i in 0..n {
        if values[i] != target {
            continue;
        }
        let (p, q) = (prev[i], next[i]);
        if p != NIL { next[p] = q; } else { head = q; }
        if q != NIL { prev[q] = p; }
        prev[i] = NIL;
        next[i] = NIL;
    }

    let mut out = Vec::new();
    let mut cur = head;
    while cur != NIL {
        out.push(values[cur]);
        cur = next[cur];
    }
    out
}
```

### Go
```go
type dllNode struct {
	val        int64
	prev, next *dllNode
}

func dllRemoveAll(values []int64, target int64) []int64 {
	var head, tail *dllNode
	for _, v := range values {
		n := &dllNode{val: v, prev: tail}
		if tail == nil {
			head = n
		} else {
			tail.next = n
		}
		tail = n
	}

	for n := head; n != nil; {
		nxt := n.next
		if n.val == target {
			if n.prev != nil {
				n.prev.next = n.next
			} else {
				head = n.next
			}
			if n.next != nil {
				n.next.prev = n.prev
			} else {
				tail = n.prev
			}
			n.prev, n.next = nil, nil
		}
		n = nxt
	}

	out := []int64{}
	for n := head; n != nil; n = n.next {
		out = append(out, n.val)
	}
	return out
}
```

### C#
```csharp
public class DllNode
{
    public long Val;
    public DllNode Prev, Next;
    public DllNode(long val) { Val = val; }
}

public static long[] DllRemoveAll(long[] values, long target)
{
    DllNode head = null, tail = null;
    foreach (long v in values)
    {
        var node = new DllNode(v);
        if (tail == null) head = node;
        else { tail.Next = node; node.Prev = tail; }
        tail = node;
    }

    DllNode cur = head;
    while (cur != null)
    {
        DllNode nxt = cur.Next;
        if (cur.Val == target)
        {
            if (cur.Prev != null) cur.Prev.Next = cur.Next;
            else head = cur.Next;
            if (cur.Next != null) cur.Next.Prev = cur.Prev;
            else tail = cur.Prev;
            cur.Prev = cur.Next = null;
        }
        cur = nxt;
    }

    var result = new List<long>();
    for (cur = head; cur != null; cur = cur.Next) result.Add(cur.Val);
    return result.ToArray();
}
```

### Ruby
```ruby
DllNode = Struct.new(:val, :prev, :next)

def dll_remove_all(values, target)
  head = tail = nil
  values.each do |v|
    node = DllNode.new(v, tail, nil)
    if tail.nil?
      head = node
    else
      tail.next = node
    end
    tail = node
  end

  node = head
  while node
    nxt = node.next
    if node.val == target
      if node.prev
        node.prev.next = node.next
      else
        head = node.next
      end
      if node.next
        node.next.prev = node.prev
      else
        tail = node.prev
      end
      node.prev = node.next = nil
    end
    node = nxt
  end

  out = []
  node = head
  while node
    out << node.val
    node = node.next
  end
  out
end
```
