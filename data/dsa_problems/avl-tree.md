---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: avl-tree
fn_python: avl_height
fn_javascript: avlHeight
fn_typescript: avlHeight
fn_java: avlHeight
fn_cpp: avl_height
fn_c: avl_height
fn_rust: avl_height
fn_go: avlHeight
fn_csharp: AvlHeight
fn_ruby: avl_height
test_cases: [{"args": [[]], "expected": 0}, {"args": [[42]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 2}, {"args": [[3, 1, 2]], "expected": 2}, {"args": [[1, 2, 3, 4, 5, 6, 7]], "expected": 3}, {"args": [[5, 5, 5]], "expected": 1}, {"args": [[10, 20, 30, 40, 50, 25]], "expected": 3}, {"args": [[7, 3, 9, 3, 7, 1]], "expected": 3}, {"args": [[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]], "expected": 4}, {"args": [[-1000000000000, 0, 1000000000000]], "expected": 2}]
---
# AVL Tree Height (Insertion) — Medium — AVL Tree

## Problem
Start with an empty AVL tree and insert the values of `values` one at a time, in the given order, using the standard AVL insertion:

1. Insert the value as in an ordinary binary search tree (smaller values go left, larger go right).
2. If the value is already in the tree, ignore it: the tree does not change for that value.
3. After each new node is added, walk back up to the root. At every node, if the left and right subtree heights differ by 2, fix it with a single or double rotation (the usual four AVL cases), so that afterwards every node's subtrees differ in height by at most 1.

Return the **height** of the final tree. The height is the number of nodes on the longest path from the root down to a leaf. An empty tree has height 0, and a tree with one node has height 1.

Values are 64-bit integers. The tree shape is fully determined by the insertion order, so the answer is unique.

## Example
values = [10, 20, 30, 40, 50, 25] → 3

Inserting 10, 20, 30 triggers a left rotation at 10 (root becomes 20). Inserting 40 and 50 triggers a left rotation at 30. Inserting 25 leaves node 20 right-heavy by 2 with a left-leaning right child, so a right-left double rotation at 40 and 20 makes 30 the root. The final tree has root 30 with children 20 and 40, and 20 has children 10 and 25 and 40 has child 50. The longest path is 30 → 20 → 10 (or 25), which has 3 nodes.

## Approach
Keep each node's height cached. After inserting into a subtree, recompute its height from its children, compute the balance factor (left height minus right height), and rotate when it is +2 or -2. For a left-heavy child, choose a double rotation if the new value went into that child's right side (left-right case); the mirror case is right-left. Each insertion costs O(log n) time and at most two rotations, and the tree height stays O(log n). Total time O(n log n) for n values; space O(n).

## Hints
- Update the height of the lower node first after a rotation. The node that moves to the top is updated last.
- Decide the rotation case by comparing the new value with the child's value, not by the child's balance factor. Equal values never reach this step because they are ignored.
- Free or drop the nodes you allocate if your language requires it; the tree is not needed after you read its height.

## Solutions
*Conventions: Java code sits in `class Solution` with static methods. C++ uses `std::` qualified names (no `using namespace std;` is assumed). C# code sits in `static class Solution`. Rust is a top-level function.*

### Python
```python
class _Node:
    __slots__ = ("v", "l", "r", "h")

    def __init__(self, v):
        self.v, self.l, self.r, self.h = v, None, None, 1


def _h(n):
    return n.h if n else 0


def _upd(n):
    n.h = 1 + max(_h(n.l), _h(n.r))


def _rot_r(y):
    x = y.l
    y.l = x.r
    x.r = y
    _upd(y)
    _upd(x)
    return x


def _rot_l(x):
    y = x.r
    x.r = y.l
    y.l = x
    _upd(x)
    _upd(y)
    return y


def _insert(n, v):
    if n is None:
        return _Node(v)
    if v < n.v:
        n.l = _insert(n.l, v)
    elif v > n.v:
        n.r = _insert(n.r, v)
    else:
        return n
    _upd(n)
    b = _h(n.l) - _h(n.r)
    if b > 1:
        if v > n.l.v:
            n.l = _rot_l(n.l)
        return _rot_r(n)
    if b < -1:
        if v < n.r.v:
            n.r = _rot_r(n.r)
        return _rot_l(n)
    return n


def avl_height(values):
    root = None
    for v in values:
        root = _insert(root, v)
    return _h(root)
```

### JavaScript
```javascript
function avlH(n) {
  return n ? n.h : 0;
}

function avlUpd(n) {
  n.h = 1 + Math.max(avlH(n.l), avlH(n.r));
}

function avlRotR(y) {
  const x = y.l;
  y.l = x.r;
  x.r = y;
  avlUpd(y);
  avlUpd(x);
  return x;
}

function avlRotL(x) {
  const y = x.r;
  x.r = y.l;
  y.l = x;
  avlUpd(x);
  avlUpd(y);
  return y;
}

function avlInsert(n, v) {
  if (n === null) return { v, l: null, r: null, h: 1 };
  if (v < n.v) n.l = avlInsert(n.l, v);
  else if (v > n.v) n.r = avlInsert(n.r, v);
  else return n;
  avlUpd(n);
  const b = avlH(n.l) - avlH(n.r);
  if (b > 1) {
    if (v > n.l.v) n.l = avlRotL(n.l);
    return avlRotR(n);
  }
  if (b < -1) {
    if (v < n.r.v) n.r = avlRotR(n.r);
    return avlRotL(n);
  }
  return n;
}

function avlHeight(values) {
  let root = null;
  for (const v of values) root = avlInsert(root, v);
  return avlH(root);
}
```

### TypeScript
```typescript
interface AvlNode {
  v: number;
  l: AvlNode | null;
  r: AvlNode | null;
  h: number;
}

function avlH(n: AvlNode | null): number {
  return n ? n.h : 0;
}

function avlUpd(n: AvlNode): void {
  n.h = 1 + Math.max(avlH(n.l), avlH(n.r));
}

function avlRotR(y: AvlNode): AvlNode {
  const x = y.l!;
  y.l = x.r;
  x.r = y;
  avlUpd(y);
  avlUpd(x);
  return x;
}

function avlRotL(x: AvlNode): AvlNode {
  const y = x.r!;
  x.r = y.l;
  y.l = x;
  avlUpd(x);
  avlUpd(y);
  return y;
}

function avlInsert(n: AvlNode | null, v: number): AvlNode {
  if (n === null) return { v, l: null, r: null, h: 1 };
  if (v < n.v) n.l = avlInsert(n.l, v);
  else if (v > n.v) n.r = avlInsert(n.r, v);
  else return n;
  avlUpd(n);
  const b = avlH(n.l) - avlH(n.r);
  if (b > 1) {
    if (v > n.l!.v) n.l = avlRotL(n.l!);
    return avlRotR(n);
  }
  if (b < -1) {
    if (v < n.r!.v) n.r = avlRotR(n.r!);
    return avlRotL(n);
  }
  return n;
}

function avlHeight(values: number[]): number {
  let root: AvlNode | null = null;
  for (const v of values) root = avlInsert(root, v);
  return avlH(root);
}
```

### Java
```java
class Solution {
    static final class AvlNode {
        long v;
        AvlNode l, r;
        int h = 1;

        AvlNode(long v) { this.v = v; }
    }

    static int avlH(AvlNode n) { return n == null ? 0 : n.h; }

    static void avlUpd(AvlNode n) { n.h = 1 + Math.max(avlH(n.l), avlH(n.r)); }

    static AvlNode avlRotR(AvlNode y) {
        AvlNode x = y.l;
        y.l = x.r;
        x.r = y;
        avlUpd(y);
        avlUpd(x);
        return x;
    }

    static AvlNode avlRotL(AvlNode x) {
        AvlNode y = x.r;
        x.r = y.l;
        y.l = x;
        avlUpd(x);
        avlUpd(y);
        return y;
    }

    static AvlNode avlInsert(AvlNode n, long v) {
        if (n == null) return new AvlNode(v);
        if (v < n.v) n.l = avlInsert(n.l, v);
        else if (v > n.v) n.r = avlInsert(n.r, v);
        else return n;
        avlUpd(n);
        int b = avlH(n.l) - avlH(n.r);
        if (b > 1) {
            if (v > n.l.v) n.l = avlRotL(n.l);
            return avlRotR(n);
        }
        if (b < -1) {
            if (v < n.r.v) n.r = avlRotR(n.r);
            return avlRotL(n);
        }
        return n;
    }

    public static long avlHeight(long[] values) {
        AvlNode root = null;
        for (long v : values) root = avlInsert(root, v);
        return avlH(root);
    }
}
```

### C++
```cpp
struct AvlNode {
    long long v;
    AvlNode *l = nullptr, *r = nullptr;
    int h = 1;
    explicit AvlNode(long long x) : v(x) {}
};

static int avl_h(const AvlNode* n) { return n ? n->h : 0; }

static void avl_upd(AvlNode* n) { n->h = 1 + std::max(avl_h(n->l), avl_h(n->r)); }

static AvlNode* avl_rot_r(AvlNode* y) {
    AvlNode* x = y->l;
    y->l = x->r;
    x->r = y;
    avl_upd(y);
    avl_upd(x);
    return x;
}

static AvlNode* avl_rot_l(AvlNode* x) {
    AvlNode* y = x->r;
    x->r = y->l;
    y->l = x;
    avl_upd(x);
    avl_upd(y);
    return y;
}

static AvlNode* avl_insert(AvlNode* n, long long v) {
    if (!n) return new AvlNode(v);
    if (v < n->v) n->l = avl_insert(n->l, v);
    else if (v > n->v) n->r = avl_insert(n->r, v);
    else return n;
    avl_upd(n);
    int b = avl_h(n->l) - avl_h(n->r);
    if (b > 1) {
        if (v > n->l->v) n->l = avl_rot_l(n->l);
        return avl_rot_r(n);
    }
    if (b < -1) {
        if (v < n->r->v) n->r = avl_rot_r(n->r);
        return avl_rot_l(n);
    }
    return n;
}

static void avl_free(AvlNode* n) {
    if (!n) return;
    avl_free(n->l);
    avl_free(n->r);
    delete n;
}

long long avl_height(const std::vector<long long>& values) {
    AvlNode* root = nullptr;
    for (long long v : values) root = avl_insert(root, v);
    long long res = avl_h(root);
    avl_free(root);
    return res;
}
```

### C
```c
#include <stdlib.h>

typedef struct AvlNode {
    long long v;
    struct AvlNode *l, *r;
    int h;
} AvlNode;

static int avl_h(const AvlNode *n) { return n ? n->h : 0; }

static void avl_upd(AvlNode *n) {
    int a = avl_h(n->l), b = avl_h(n->r);
    n->h = 1 + (a > b ? a : b);
}

static AvlNode *avl_rot_r(AvlNode *y) {
    AvlNode *x = y->l;
    y->l = x->r;
    x->r = y;
    avl_upd(y);
    avl_upd(x);
    return x;
}

static AvlNode *avl_rot_l(AvlNode *x) {
    AvlNode *y = x->r;
    x->r = y->l;
    y->l = x;
    avl_upd(x);
    avl_upd(y);
    return y;
}

static AvlNode *avl_insert(AvlNode *n, long long v) {
    if (!n) {
        n = malloc(sizeof *n);
        n->v = v;
        n->l = n->r = NULL;
        n->h = 1;
        return n;
    }
    if (v < n->v) n->l = avl_insert(n->l, v);
    else if (v > n->v) n->r = avl_insert(n->r, v);
    else return n;
    avl_upd(n);
    int b = avl_h(n->l) - avl_h(n->r);
    if (b > 1) {
        if (v > n->l->v) n->l = avl_rot_l(n->l);
        return avl_rot_r(n);
    }
    if (b < -1) {
        if (v < n->r->v) n->r = avl_rot_r(n->r);
        return avl_rot_l(n);
    }
    return n;
}

static void avl_free(AvlNode *n) {
    if (!n) return;
    avl_free(n->l);
    avl_free(n->r);
    free(n);
}

long long avl_height(long long *values, int valuesSize) {
    AvlNode *root = NULL;
    for (int i = 0; i < valuesSize; i++) root = avl_insert(root, values[i]);
    long long res = avl_h(root);
    avl_free(root);
    return res;
}
```

### Rust
```rust
struct AvlNode {
    v: i64,
    h: i64,
    l: Option<Box<AvlNode>>,
    r: Option<Box<AvlNode>>,
}

fn avl_h(n: &Option<Box<AvlNode>>) -> i64 {
    n.as_ref().map_or(0, |n| n.h)
}

fn avl_upd(n: &mut AvlNode) {
    n.h = 1 + avl_h(&n.l).max(avl_h(&n.r));
}

fn avl_rot_r(mut y: Box<AvlNode>) -> Box<AvlNode> {
    let mut x = y.l.take().unwrap();
    y.l = x.r.take();
    avl_upd(&mut y);
    x.r = Some(y);
    avl_upd(&mut x);
    x
}

fn avl_rot_l(mut x: Box<AvlNode>) -> Box<AvlNode> {
    let mut y = x.r.take().unwrap();
    x.r = y.l.take();
    avl_upd(&mut x);
    y.l = Some(x);
    avl_upd(&mut y);
    y
}

fn avl_insert(node: Option<Box<AvlNode>>, v: i64) -> Box<AvlNode> {
    let mut n = match node {
        None => return Box::new(AvlNode { v, h: 1, l: None, r: None }),
        Some(n) => n,
    };
    if v < n.v {
        n.l = Some(avl_insert(n.l.take(), v));
    } else if v > n.v {
        n.r = Some(avl_insert(n.r.take(), v));
    } else {
        return n;
    }
    avl_upd(&mut n);
    let b = avl_h(&n.l) - avl_h(&n.r);
    if b > 1 {
        if v > n.l.as_ref().unwrap().v {
            let l = n.l.take().unwrap();
            n.l = Some(avl_rot_l(l));
        }
        return avl_rot_r(n);
    }
    if b < -1 {
        if v < n.r.as_ref().unwrap().v {
            let r = n.r.take().unwrap();
            n.r = Some(avl_rot_r(r));
        }
        return avl_rot_l(n);
    }
    n
}

pub fn avl_height(values: Vec<i64>) -> i64 {
    let mut root: Option<Box<AvlNode>> = None;
    for v in values {
        root = Some(avl_insert(root, v));
    }
    avl_h(&root)
}
```

### Go
```go
type avlNode struct {
	v    int64
	h    int
	l, r *avlNode
}

func avlH(n *avlNode) int {
	if n == nil {
		return 0
	}
	return n.h
}

func avlUpd(n *avlNode) {
	a, b := avlH(n.l), avlH(n.r)
	if a > b {
		n.h = 1 + a
	} else {
		n.h = 1 + b
	}
}

func avlRotR(y *avlNode) *avlNode {
	x := y.l
	y.l = x.r
	x.r = y
	avlUpd(y)
	avlUpd(x)
	return x
}

func avlRotL(x *avlNode) *avlNode {
	y := x.r
	x.r = y.l
	y.l = x
	avlUpd(x)
	avlUpd(y)
	return y
}

func avlInsert(n *avlNode, v int64) *avlNode {
	if n == nil {
		return &avlNode{v: v, h: 1}
	}
	if v < n.v {
		n.l = avlInsert(n.l, v)
	} else if v > n.v {
		n.r = avlInsert(n.r, v)
	} else {
		return n
	}
	avlUpd(n)
	b := avlH(n.l) - avlH(n.r)
	if b > 1 {
		if v > n.l.v {
			n.l = avlRotL(n.l)
		}
		return avlRotR(n)
	}
	if b < -1 {
		if v < n.r.v {
			n.r = avlRotR(n.r)
		}
		return avlRotL(n)
	}
	return n
}

func avlHeight(values []int64) int64 {
	var root *avlNode
	for _, v := range values {
		root = avlInsert(root, v)
	}
	return int64(avlH(root))
}
```

### C#
```csharp
public static class Solution {
    private sealed class AvlNode {
        public long V;
        public AvlNode? L, R;
        public int H = 1;

        public AvlNode(long v) { V = v; }
    }

    private static int Height(AvlNode? n) => n == null ? 0 : n.H;

    private static void Upd(AvlNode n) { n.H = 1 + Math.Max(Height(n.L), Height(n.R)); }

    private static AvlNode RotR(AvlNode y) {
        AvlNode x = y.L!;
        y.L = x.R;
        x.R = y;
        Upd(y);
        Upd(x);
        return x;
    }

    private static AvlNode RotL(AvlNode x) {
        AvlNode y = x.R!;
        x.R = y.L;
        y.L = x;
        Upd(x);
        Upd(y);
        return y;
    }

    private static AvlNode Insert(AvlNode? n, long v) {
        if (n == null) return new AvlNode(v);
        if (v < n.V) n.L = Insert(n.L, v);
        else if (v > n.V) n.R = Insert(n.R, v);
        else return n;
        Upd(n);
        int b = Height(n.L) - Height(n.R);
        if (b > 1) {
            if (v > n.L!.V) n.L = RotL(n.L);
            return RotR(n);
        }
        if (b < -1) {
            if (v < n.R!.V) n.R = RotR(n.R);
            return RotL(n);
        }
        return n;
    }

    public static long AvlHeight(long[] values) {
        AvlNode? root = null;
        foreach (long v in values) root = Insert(root, v);
        return Height(root);
    }
}
```

### Ruby
```ruby
AvlNode = Struct.new(:v, :l, :r, :h)

def avl_h(n)
  n ? n.h : 0
end

def avl_upd(n)
  n.h = 1 + [avl_h(n.l), avl_h(n.r)].max
end

def avl_rot_r(y)
  x = y.l
  y.l = x.r
  x.r = y
  avl_upd(y)
  avl_upd(x)
  x
end

def avl_rot_l(x)
  y = x.r
  x.r = y.l
  y.l = x
  avl_upd(x)
  avl_upd(y)
  y
end

def avl_insert(n, v)
  return AvlNode.new(v, nil, nil, 1) if n.nil?
  if v < n.v
    n.l = avl_insert(n.l, v)
  elsif v > n.v
    n.r = avl_insert(n.r, v)
  else
    return n
  end
  avl_upd(n)
  b = avl_h(n.l) - avl_h(n.r)
  if b > 1
    n.l = avl_rot_l(n.l) if v > n.l.v
    return avl_rot_r(n)
  end
  if b < -1
    n.r = avl_rot_r(n.r) if v < n.r.v
    return avl_rot_l(n)
  end
  n
end

def avl_height(values)
  root = nil
  values.each { |v| root = avl_insert(root, v) }
  avl_h(root)
end
```
