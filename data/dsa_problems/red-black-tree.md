---
track: dsa
difficulty: Hard
source: authored
io_mode: function
algorithms: red-black-tree
fn_python: rb_black_height
fn_javascript: rbBlackHeight
fn_typescript: rbBlackHeight
fn_java: rbBlackHeight
fn_cpp: rb_black_height
fn_c: rb_black_height
fn_rust: rb_black_height
fn_go: rbBlackHeight
fn_csharp: RbBlackHeight
fn_ruby: rb_black_height
test_cases: [{"args": [[]], "expected": 0}, {"args": [[7]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 1}, {"args": [[5, 5, 5]], "expected": 1}, {"args": [[1, 2, 3, 4, 5, 6, 7]], "expected": 2}, {"args": [[10, 20, 30, 15, 25, 5, 1]], "expected": 2}, {"args": [[41, 38, 31, 12, 19, 8]], "expected": 2}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]], "expected": 3}, {"args": [[-3, 0, 8, -1000000000, 1000000000, 42, 42, 17]], "expected": 2}]
---
# Red-black tree black height — Hard — Data Structure

## Problem
Start with an empty red-black tree and insert the integers of `values` one at a time, in the given order, using the CLRS insertion algorithm:

- Each new node is coloured red. Walk down from the root, going left when the new key is less than the current node's key and right otherwise (so an equal key goes right). Attach the new node as a leaf.
- Then repeatedly recolour and rotate (CLRS `RB-INSERT-FIXUP`) until no red node has a red child and the root is black.

The **black height** of the resulting tree is the number of black nodes on its **leftmost path**: start at the root, repeatedly move to the left child, and count every black node visited, stopping when the left child is the NIL leaf. The root is counted when the tree is non-empty; NIL leaves are never counted.

Return the black height. An empty `values` returns 0.

Input: `values` (int[], 0 to 100000 elements, each in [-10^9, 10^9]). Output: int.

## Example
values = [1, 2, 3] → 1

Inserting 1 and 2 gives a black root 1 with a red right child 2. Inserting 3 makes two reds in a row on the right, so the uncle (NIL) is black and the fix-up rotates left at 1. The root is now 2 (black), with children 1 (red) and 3 (red). The leftmost path is 2 (black), 1 (red), NIL, so the count is 1.

## Approach
Simulate CLRS insertion on node arrays where index 0 is the shared black NIL sentinel. Each insert does a standard BST descent, attaches a red node, and runs the fix-up loop: a red uncle means recolour and move up; a black uncle means at most one double rotation, then stop. After all inserts, walk the leftmost path and count black nodes. Time O(n log n), space O(n).

## Hints
- Keep NIL as an index with colour black and never write to its parent; guard the parent update in rotations.
- Equal keys must go right in both the descent and the attach step, or the tree shape (and the answer) changes.
- The loop condition `color[parent[z]] == RED` stops at the root, because the root's parent is NIL and NIL is black.
- Only count the root and real nodes; do not count the NIL at the end of the path.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code is an instance method; its helper class is nested inside `Solution`. C# is placed in `public static class Solution`. Go and Ruby are plain functions.*

### Python
```python
RED, BLACK = 0, 1
NIL = 0

def rb_black_height(values):
    key = [0]; color = [BLACK]; left = [NIL]; right = [NIL]; parent = [NIL]
    state = {"root": NIL}

    def new_node(k):
        key.append(k); color.append(RED); left.append(NIL); right.append(NIL); parent.append(NIL)
        return len(key) - 1

    def rotate_left(x):
        y = right[x]
        right[x] = left[y]
        if left[y] != NIL:
            parent[left[y]] = x
        parent[y] = parent[x]
        if parent[x] == NIL:
            state["root"] = y
        elif x == left[parent[x]]:
            left[parent[x]] = y
        else:
            right[parent[x]] = y
        left[y] = x
        parent[x] = y

    def rotate_right(x):
        y = left[x]
        left[x] = right[y]
        if right[y] != NIL:
            parent[right[y]] = x
        parent[y] = parent[x]
        if parent[x] == NIL:
            state["root"] = y
        elif x == right[parent[x]]:
            right[parent[x]] = y
        else:
            left[parent[x]] = y
        right[y] = x
        parent[x] = y

    def insert(k):
        z = new_node(k)
        y, x = NIL, state["root"]
        while x != NIL:
            y = x
            x = left[x] if k < key[x] else right[x]
        parent[z] = y
        if y == NIL:
            state["root"] = z
        elif k < key[y]:
            left[y] = z
        else:
            right[y] = z
        while color[parent[z]] == RED:
            p = parent[z]
            g = parent[p]
            if p == left[g]:
                u = right[g]
                if color[u] == RED:
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED
                    z = g
                else:
                    if z == right[p]:
                        z = p
                        rotate_left(z)
                    p = parent[z]; g = parent[p]
                    color[p] = BLACK; color[g] = RED
                    rotate_right(g)
            else:
                u = left[g]
                if color[u] == RED:
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED
                    z = g
                else:
                    if z == left[p]:
                        z = p
                        rotate_right(z)
                    p = parent[z]; g = parent[p]
                    color[p] = BLACK; color[g] = RED
                    rotate_left(g)
        color[state["root"]] = BLACK

    for v in values:
        insert(v)
    count = 0
    x = state["root"]
    while x != NIL:
        if color[x] == BLACK:
            count += 1
        x = left[x]
    return count
```

### JavaScript
```javascript
function rbBlackHeight(values) {
  const RED = 0, BLACK = 1, NIL = 0;
  const key = [0], color = [BLACK], left = [NIL], right = [NIL], parent = [NIL];
  let root = NIL;

  const newNode = (k) => {
    key.push(k); color.push(RED); left.push(NIL); right.push(NIL); parent.push(NIL);
    return key.length - 1;
  };

  const rotateLeft = (x) => {
    const y = right[x];
    right[x] = left[y];
    if (left[y] !== NIL) parent[left[y]] = x;
    parent[y] = parent[x];
    if (parent[x] === NIL) root = y;
    else if (x === left[parent[x]]) left[parent[x]] = y;
    else right[parent[x]] = y;
    left[y] = x;
    parent[x] = y;
  };

  const rotateRight = (x) => {
    const y = left[x];
    left[x] = right[y];
    if (right[y] !== NIL) parent[right[y]] = x;
    parent[y] = parent[x];
    if (parent[x] === NIL) root = y;
    else if (x === right[parent[x]]) right[parent[x]] = y;
    else left[parent[x]] = y;
    right[y] = x;
    parent[x] = y;
  };

  const insert = (k) => {
    let z = newNode(k);
    let y = NIL, x = root;
    while (x !== NIL) {
      y = x;
      x = k < key[x] ? left[x] : right[x];
    }
    parent[z] = y;
    if (y === NIL) root = z;
    else if (k < key[y]) left[y] = z;
    else right[y] = z;
    while (color[parent[z]] === RED) {
      let p = parent[z], g = parent[p];
      if (p === left[g]) {
        const u = right[g];
        if (color[u] === RED) {
          color[p] = BLACK; color[u] = BLACK; color[g] = RED;
          z = g;
        } else {
          if (z === right[p]) { z = p; rotateLeft(z); }
          p = parent[z]; g = parent[p];
          color[p] = BLACK; color[g] = RED;
          rotateRight(g);
        }
      } else {
        const u = left[g];
        if (color[u] === RED) {
          color[p] = BLACK; color[u] = BLACK; color[g] = RED;
          z = g;
        } else {
          if (z === left[p]) { z = p; rotateRight(z); }
          p = parent[z]; g = parent[p];
          color[p] = BLACK; color[g] = RED;
          rotateLeft(g);
        }
      }
    }
    color[root] = BLACK;
  };

  for (const v of values) insert(v);
  let count = 0;
  for (let x = root; x !== NIL; x = left[x]) {
    if (color[x] === BLACK) count++;
  }
  return count;
}
```

### TypeScript
```typescript
function rbBlackHeight(values: number[]): number {
  const RED = 0, BLACK = 1, NIL = 0;
  const key: number[] = [0];
  const color: number[] = [BLACK];
  const left: number[] = [NIL];
  const right: number[] = [NIL];
  const parent: number[] = [NIL];
  let root = NIL;

  const newNode = (k: number): number => {
    key.push(k); color.push(RED); left.push(NIL); right.push(NIL); parent.push(NIL);
    return key.length - 1;
  };

  const rotateLeft = (x: number): void => {
    const y = right[x];
    right[x] = left[y];
    if (left[y] !== NIL) parent[left[y]] = x;
    parent[y] = parent[x];
    if (parent[x] === NIL) root = y;
    else if (x === left[parent[x]]) left[parent[x]] = y;
    else right[parent[x]] = y;
    left[y] = x;
    parent[x] = y;
  };

  const rotateRight = (x: number): void => {
    const y = left[x];
    left[x] = right[y];
    if (right[y] !== NIL) parent[right[y]] = x;
    parent[y] = parent[x];
    if (parent[x] === NIL) root = y;
    else if (x === right[parent[x]]) right[parent[x]] = y;
    else left[parent[x]] = y;
    right[y] = x;
    parent[x] = y;
  };

  const insert = (k: number): void => {
    let z = newNode(k);
    let y = NIL, x = root;
    while (x !== NIL) {
      y = x;
      x = k < key[x] ? left[x] : right[x];
    }
    parent[z] = y;
    if (y === NIL) root = z;
    else if (k < key[y]) left[y] = z;
    else right[y] = z;
    while (color[parent[z]] === RED) {
      let p = parent[z], g = parent[p];
      if (p === left[g]) {
        const u = right[g];
        if (color[u] === RED) {
          color[p] = BLACK; color[u] = BLACK; color[g] = RED;
          z = g;
        } else {
          if (z === right[p]) { z = p; rotateLeft(z); }
          p = parent[z]; g = parent[p];
          color[p] = BLACK; color[g] = RED;
          rotateRight(g);
        }
      } else {
        const u = left[g];
        if (color[u] === RED) {
          color[p] = BLACK; color[u] = BLACK; color[g] = RED;
          z = g;
        } else {
          if (z === left[p]) { z = p; rotateRight(z); }
          p = parent[z]; g = parent[p];
          color[p] = BLACK; color[g] = RED;
          rotateLeft(g);
        }
      }
    }
    color[root] = BLACK;
  };

  for (const v of values) insert(v);
  let count = 0;
  for (let x = root; x !== NIL; x = left[x]) {
    if (color[x] === BLACK) count++;
  }
  return count;
}
```

### Java
```java
public int rbBlackHeight(int[] values) {
    RBTree t = new RBTree(values.length);
    for (int v : values) {
        t.insert(v);
    }
    return t.leftmostBlackCount();
}

private static final class RBTree {
    private static final int RED = 0, BLACK = 1, NIL = 0;
    private final int[] key, color, left, right, parent;
    private int used = 0;
    private int root = NIL;

    RBTree(int capacity) {
        key = new int[capacity + 1];
        color = new int[capacity + 1];
        left = new int[capacity + 1];
        right = new int[capacity + 1];
        parent = new int[capacity + 1];
        color[NIL] = BLACK;
    }

    private void rotateLeft(int x) {
        int y = right[x];
        right[x] = left[y];
        if (left[y] != NIL) parent[left[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == NIL) root = y;
        else if (x == left[parent[x]]) left[parent[x]] = y;
        else right[parent[x]] = y;
        left[y] = x;
        parent[x] = y;
    }

    private void rotateRight(int x) {
        int y = left[x];
        left[x] = right[y];
        if (right[y] != NIL) parent[right[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == NIL) root = y;
        else if (x == right[parent[x]]) right[parent[x]] = y;
        else left[parent[x]] = y;
        right[y] = x;
        parent[x] = y;
    }

    void insert(int k) {
        int z = ++used;
        key[z] = k;
        color[z] = RED;
        left[z] = NIL;
        right[z] = NIL;
        parent[z] = NIL;
        int y = NIL, x = root;
        while (x != NIL) {
            y = x;
            x = k < key[x] ? left[x] : right[x];
        }
        parent[z] = y;
        if (y == NIL) root = z;
        else if (k < key[y]) left[y] = z;
        else right[y] = z;
        while (color[parent[z]] == RED) {
            int p = parent[z], g = parent[p];
            if (p == left[g]) {
                int u = right[g];
                if (color[u] == RED) {
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED;
                    z = g;
                } else {
                    if (z == right[p]) { z = p; rotateLeft(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = BLACK; color[g] = RED;
                    rotateRight(g);
                }
            } else {
                int u = left[g];
                if (color[u] == RED) {
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED;
                    z = g;
                } else {
                    if (z == left[p]) { z = p; rotateRight(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = BLACK; color[g] = RED;
                    rotateLeft(g);
                }
            }
        }
        color[root] = BLACK;
    }

    int leftmostBlackCount() {
        int count = 0;
        for (int x = root; x != NIL; x = left[x]) {
            if (color[x] == BLACK) count++;
        }
        return count;
    }
}
```

### C++
```cpp
struct RBTree {
    enum : int { RED = 0, BLACK = 1, NIL = 0 };
    std::vector<int> key, color, left, right, parent;
    int used = 0;
    int root = NIL;

    explicit RBTree(size_t capacity)
        : key(capacity + 1, 0), color(capacity + 1, BLACK), left(capacity + 1, NIL),
          right(capacity + 1, NIL), parent(capacity + 1, NIL) {}

    void rotate_left(int x) {
        int y = right[x];
        right[x] = left[y];
        if (left[y] != NIL) parent[left[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == NIL) root = y;
        else if (x == left[parent[x]]) left[parent[x]] = y;
        else right[parent[x]] = y;
        left[y] = x;
        parent[x] = y;
    }

    void rotate_right(int x) {
        int y = left[x];
        left[x] = right[y];
        if (right[y] != NIL) parent[right[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == NIL) root = y;
        else if (x == right[parent[x]]) right[parent[x]] = y;
        else left[parent[x]] = y;
        right[y] = x;
        parent[x] = y;
    }

    void insert(int k) {
        int z = ++used;
        key[z] = k; color[z] = RED; left[z] = NIL; right[z] = NIL; parent[z] = NIL;
        int y = NIL, x = root;
        while (x != NIL) {
            y = x;
            x = k < key[x] ? left[x] : right[x];
        }
        parent[z] = y;
        if (y == NIL) root = z;
        else if (k < key[y]) left[y] = z;
        else right[y] = z;
        while (color[parent[z]] == RED) {
            int p = parent[z], g = parent[p];
            if (p == left[g]) {
                int u = right[g];
                if (color[u] == RED) {
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED;
                    z = g;
                } else {
                    if (z == right[p]) { z = p; rotate_left(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = BLACK; color[g] = RED;
                    rotate_right(g);
                }
            } else {
                int u = left[g];
                if (color[u] == RED) {
                    color[p] = BLACK; color[u] = BLACK; color[g] = RED;
                    z = g;
                } else {
                    if (z == left[p]) { z = p; rotate_right(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = BLACK; color[g] = RED;
                    rotate_left(g);
                }
            }
        }
        color[root] = BLACK;
    }

    int leftmost_black_count() const {
        int count = 0;
        for (int x = root; x != NIL; x = left[x]) {
            if (color[x] == BLACK) count++;
        }
        return count;
    }
};

int rb_black_height(std::vector<int>& values) {
    RBTree t(values.size());
    for (int v : values) t.insert(v);
    return t.leftmost_black_count();
}
```

### C
```c
typedef struct {
    int *key, *color, *left, *right, *parent;
    int used;
    int root;
} RBTree;

enum { RB_RED = 0, RB_BLACK = 1, RB_NIL = 0 };

static void rb_rotate_left(RBTree *t, int x) {
    int y = t->right[x];
    t->right[x] = t->left[y];
    if (t->left[y] != RB_NIL) t->parent[t->left[y]] = x;
    t->parent[y] = t->parent[x];
    if (t->parent[x] == RB_NIL) t->root = y;
    else if (x == t->left[t->parent[x]]) t->left[t->parent[x]] = y;
    else t->right[t->parent[x]] = y;
    t->left[y] = x;
    t->parent[x] = y;
}

static void rb_rotate_right(RBTree *t, int x) {
    int y = t->left[x];
    t->left[x] = t->right[y];
    if (t->right[y] != RB_NIL) t->parent[t->right[y]] = x;
    t->parent[y] = t->parent[x];
    if (t->parent[x] == RB_NIL) t->root = y;
    else if (x == t->right[t->parent[x]]) t->right[t->parent[x]] = y;
    else t->left[t->parent[x]] = y;
    t->right[y] = x;
    t->parent[x] = y;
}

static void rb_insert(RBTree *t, int k) {
    int z = ++t->used;
    t->key[z] = k;
    t->color[z] = RB_RED;
    t->left[z] = RB_NIL;
    t->right[z] = RB_NIL;
    t->parent[z] = RB_NIL;
    int y = RB_NIL, x = t->root;
    while (x != RB_NIL) {
        y = x;
        x = k < t->key[x] ? t->left[x] : t->right[x];
    }
    t->parent[z] = y;
    if (y == RB_NIL) t->root = z;
    else if (k < t->key[y]) t->left[y] = z;
    else t->right[y] = z;
    while (t->color[t->parent[z]] == RB_RED) {
        int p = t->parent[z], g = t->parent[p];
        if (p == t->left[g]) {
            int u = t->right[g];
            if (t->color[u] == RB_RED) {
                t->color[p] = RB_BLACK; t->color[u] = RB_BLACK; t->color[g] = RB_RED;
                z = g;
            } else {
                if (z == t->right[p]) { z = p; rb_rotate_left(t, z); }
                p = t->parent[z]; g = t->parent[p];
                t->color[p] = RB_BLACK; t->color[g] = RB_RED;
                rb_rotate_right(t, g);
            }
        } else {
            int u = t->left[g];
            if (t->color[u] == RB_RED) {
                t->color[p] = RB_BLACK; t->color[u] = RB_BLACK; t->color[g] = RB_RED;
                z = g;
            } else {
                if (z == t->left[p]) { z = p; rb_rotate_right(t, z); }
                p = t->parent[z]; g = t->parent[p];
                t->color[p] = RB_BLACK; t->color[g] = RB_RED;
                rb_rotate_left(t, g);
            }
        }
    }
    t->color[t->root] = RB_BLACK;
}

int rb_black_height(int *values, int valuesSize) {
    RBTree t;
    t.key = calloc(valuesSize + 1, sizeof(int));
    t.color = calloc(valuesSize + 1, sizeof(int));
    t.left = calloc(valuesSize + 1, sizeof(int));
    t.right = calloc(valuesSize + 1, sizeof(int));
    t.parent = calloc(valuesSize + 1, sizeof(int));
    t.used = 0;
    t.root = RB_NIL;
    t.color[RB_NIL] = RB_BLACK;
    for (int i = 0; i < valuesSize; i++) rb_insert(&t, values[i]);
    int count = 0;
    for (int x = t.root; x != RB_NIL; x = t.left[x]) {
        if (t.color[x] == RB_BLACK) count++;
    }
    free(t.key); free(t.color); free(t.left); free(t.right); free(t.parent);
    return count;
}
```

### Rust
```rust
const RED: u8 = 0;
const BLACK: u8 = 1;
const NIL: usize = 0;

struct RbTree {
    key: Vec<i32>,
    color: Vec<u8>,
    left: Vec<usize>,
    right: Vec<usize>,
    parent: Vec<usize>,
    used: usize,
    root: usize,
}

impl RbTree {
    fn new(capacity: usize) -> Self {
        let mut color = vec![RED; capacity + 1];
        color[NIL] = BLACK;
        RbTree {
            key: vec![0; capacity + 1],
            color,
            left: vec![NIL; capacity + 1],
            right: vec![NIL; capacity + 1],
            parent: vec![NIL; capacity + 1],
            used: 0,
            root: NIL,
        }
    }

    fn rotate_left(&mut self, x: usize) {
        let y = self.right[x];
        self.right[x] = self.left[y];
        if self.left[y] != NIL {
            let c = self.left[y];
            self.parent[c] = x;
        }
        self.parent[y] = self.parent[x];
        let px = self.parent[x];
        if px == NIL {
            self.root = y;
        } else if x == self.left[px] {
            self.left[px] = y;
        } else {
            self.right[px] = y;
        }
        self.left[y] = x;
        self.parent[x] = y;
    }

    fn rotate_right(&mut self, x: usize) {
        let y = self.left[x];
        self.left[x] = self.right[y];
        if self.right[y] != NIL {
            let c = self.right[y];
            self.parent[c] = x;
        }
        self.parent[y] = self.parent[x];
        let px = self.parent[x];
        if px == NIL {
            self.root = y;
        } else if x == self.right[px] {
            self.right[px] = y;
        } else {
            self.left[px] = y;
        }
        self.right[y] = x;
        self.parent[x] = y;
    }

    fn insert(&mut self, k: i32) {
        self.used += 1;
        let mut z = self.used;
        self.key[z] = k;
        self.color[z] = RED;
        self.left[z] = NIL;
        self.right[z] = NIL;
        self.parent[z] = NIL;
        let mut y = NIL;
        let mut x = self.root;
        while x != NIL {
            y = x;
            x = if k < self.key[x] { self.left[x] } else { self.right[x] };
        }
        self.parent[z] = y;
        if y == NIL {
            self.root = z;
        } else if k < self.key[y] {
            self.left[y] = z;
        } else {
            self.right[y] = z;
        }
        while self.color[self.parent[z]] == RED {
            let mut p = self.parent[z];
            let mut g = self.parent[p];
            if p == self.left[g] {
                let u = self.right[g];
                if self.color[u] == RED {
                    self.color[p] = BLACK;
                    self.color[u] = BLACK;
                    self.color[g] = RED;
                    z = g;
                } else {
                    if z == self.right[p] {
                        z = p;
                        self.rotate_left(z);
                    }
                    p = self.parent[z];
                    g = self.parent[p];
                    self.color[p] = BLACK;
                    self.color[g] = RED;
                    self.rotate_right(g);
                }
            } else {
                let u = self.left[g];
                if self.color[u] == RED {
                    self.color[p] = BLACK;
                    self.color[u] = BLACK;
                    self.color[g] = RED;
                    z = g;
                } else {
                    if z == self.left[p] {
                        z = p;
                        self.rotate_right(z);
                    }
                    p = self.parent[z];
                    g = self.parent[p];
                    self.color[p] = BLACK;
                    self.color[g] = RED;
                    self.rotate_left(g);
                }
            }
        }
        let r = self.root;
        self.color[r] = BLACK;
    }

    fn leftmost_black_count(&self) -> i32 {
        let mut count = 0;
        let mut x = self.root;
        while x != NIL {
            if self.color[x] == BLACK {
                count += 1;
            }
            x = self.left[x];
        }
        count
    }
}

pub fn rb_black_height(values: Vec<i32>) -> i32 {
    let mut t = RbTree::new(values.len());
    for v in values {
        t.insert(v);
    }
    t.leftmost_black_count()
}
```

### Go
```go
func rbBlackHeight(values []int) int {
	const red, black = 0, 1
	const nilNode = 0
	n := len(values)
	key := make([]int, n+1)
	color := make([]int, n+1)
	left := make([]int, n+1)
	right := make([]int, n+1)
	parent := make([]int, n+1)
	color[nilNode] = black
	root := nilNode
	used := 0

	rotateLeft := func(x int) {
		y := right[x]
		right[x] = left[y]
		if left[y] != nilNode {
			parent[left[y]] = x
		}
		parent[y] = parent[x]
		if parent[x] == nilNode {
			root = y
		} else if x == left[parent[x]] {
			left[parent[x]] = y
		} else {
			right[parent[x]] = y
		}
		left[y] = x
		parent[x] = y
	}

	rotateRight := func(x int) {
		y := left[x]
		left[x] = right[y]
		if right[y] != nilNode {
			parent[right[y]] = x
		}
		parent[y] = parent[x]
		if parent[x] == nilNode {
			root = y
		} else if x == right[parent[x]] {
			right[parent[x]] = y
		} else {
			left[parent[x]] = y
		}
		right[y] = x
		parent[x] = y
	}

	for _, k := range values {
		used++
		z := used
		key[z] = k
		color[z] = red
		left[z] = nilNode
		right[z] = nilNode
		parent[z] = nilNode
		y, x := nilNode, root
		for x != nilNode {
			y = x
			if k < key[x] {
				x = left[x]
			} else {
				x = right[x]
			}
		}
		parent[z] = y
		if y == nilNode {
			root = z
		} else if k < key[y] {
			left[y] = z
		} else {
			right[y] = z
		}
		for color[parent[z]] == red {
			p := parent[z]
			g := parent[p]
			if p == left[g] {
				u := right[g]
				if color[u] == red {
					color[p] = black
					color[u] = black
					color[g] = red
					z = g
				} else {
					if z == right[p] {
						z = p
						rotateLeft(z)
					}
					p = parent[z]
					g = parent[p]
					color[p] = black
					color[g] = red
					rotateRight(g)
				}
			} else {
				u := left[g]
				if color[u] == red {
					color[p] = black
					color[u] = black
					color[g] = red
					z = g
				} else {
					if z == left[p] {
						z = p
						rotateRight(z)
					}
					p = parent[z]
					g = parent[p]
					color[p] = black
					color[g] = red
					rotateLeft(g)
				}
			}
		}
		color[root] = black
	}

	count := 0
	for x := root; x != nilNode; x = left[x] {
		if color[x] == black {
			count++
		}
	}
	return count
}
```

### C#
```csharp
public static int RbBlackHeight(int[] values)
{
    const int Red = 0, Black = 1, Nil = 0;
    int n = values.Length;
    var key = new int[n + 1];
    var color = new int[n + 1];
    var left = new int[n + 1];
    var right = new int[n + 1];
    var parent = new int[n + 1];
    color[Nil] = Black;
    int root = Nil;
    int used = 0;

    void RotateLeft(int x)
    {
        int y = right[x];
        right[x] = left[y];
        if (left[y] != Nil) parent[left[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == Nil) root = y;
        else if (x == left[parent[x]]) left[parent[x]] = y;
        else right[parent[x]] = y;
        left[y] = x;
        parent[x] = y;
    }

    void RotateRight(int x)
    {
        int y = left[x];
        left[x] = right[y];
        if (right[y] != Nil) parent[right[y]] = x;
        parent[y] = parent[x];
        if (parent[x] == Nil) root = y;
        else if (x == right[parent[x]]) right[parent[x]] = y;
        else left[parent[x]] = y;
        right[y] = x;
        parent[x] = y;
    }

    foreach (int k in values)
    {
        used++;
        int z = used;
        key[z] = k;
        color[z] = Red;
        left[z] = Nil;
        right[z] = Nil;
        parent[z] = Nil;
        int y = Nil, x = root;
        while (x != Nil)
        {
            y = x;
            x = k < key[x] ? left[x] : right[x];
        }
        parent[z] = y;
        if (y == Nil) root = z;
        else if (k < key[y]) left[y] = z;
        else right[y] = z;
        while (color[parent[z]] == Red)
        {
            int p = parent[z], g = parent[p];
            if (p == left[g])
            {
                int u = right[g];
                if (color[u] == Red)
                {
                    color[p] = Black; color[u] = Black; color[g] = Red;
                    z = g;
                }
                else
                {
                    if (z == right[p]) { z = p; RotateLeft(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = Black; color[g] = Red;
                    RotateRight(g);
                }
            }
            else
            {
                int u = left[g];
                if (color[u] == Red)
                {
                    color[p] = Black; color[u] = Black; color[g] = Red;
                    z = g;
                }
                else
                {
                    if (z == left[p]) { z = p; RotateRight(z); }
                    p = parent[z]; g = parent[p];
                    color[p] = Black; color[g] = Red;
                    RotateLeft(g);
                }
            }
        }
        color[root] = Black;
    }

    int count = 0;
    for (int x = root; x != Nil; x = left[x])
    {
        if (color[x] == Black) count++;
    }
    return count;
}
```

### Ruby
```ruby
def rb_black_height(values)
  red = 0
  black = 1
  n = values.length
  key = Array.new(n + 1, 0)
  color = Array.new(n + 1, red)
  left = Array.new(n + 1, 0)
  right = Array.new(n + 1, 0)
  parent = Array.new(n + 1, 0)
  color[0] = black
  root = 0
  used = 0

  rotate_left = lambda do |x|
    y = right[x]
    right[x] = left[y]
    parent[left[y]] = x if left[y] != 0
    parent[y] = parent[x]
    if parent[x] == 0
      root = y
    elsif x == left[parent[x]]
      left[parent[x]] = y
    else
      right[parent[x]] = y
    end
    left[y] = x
    parent[x] = y
  end

  rotate_right = lambda do |x|
    y = left[x]
    left[x] = right[y]
    parent[right[y]] = x if right[y] != 0
    parent[y] = parent[x]
    if parent[x] == 0
      root = y
    elsif x == right[parent[x]]
      right[parent[x]] = y
    else
      left[parent[x]] = y
    end
    right[y] = x
    parent[x] = y
  end

  values.each do |k|
    used += 1
    z = used
    key[z] = k
    color[z] = red
    left[z] = 0
    right[z] = 0
    parent[z] = 0
    y = 0
    x = root
    while x != 0
      y = x
      x = k < key[x] ? left[x] : right[x]
    end
    parent[z] = y
    if y == 0
      root = z
    elsif k < key[y]
      left[y] = z
    else
      right[y] = z
    end
    while color[parent[z]] == red
      p = parent[z]
      g = parent[p]
      if p == left[g]
        u = right[g]
        if color[u] == red
          color[p] = black
          color[u] = black
          color[g] = red
          z = g
        else
          if z == right[p]
            z = p
            rotate_left.call(z)
          end
          p = parent[z]
          g = parent[p]
          color[p] = black
          color[g] = red
          rotate_right.call(g)
        end
      else
        u = left[g]
        if color[u] == red
          color[p] = black
          color[u] = black
          color[g] = red
          z = g
        else
          if z == left[p]
            z = p
            rotate_right.call(z)
          end
          p = parent[z]
          g = parent[p]
          color[p] = black
          color[g] = red
          rotate_left.call(g)
        end
      end
    end
    color[root] = black
  end

  count = 0
  x = root
  while x != 0
    count += 1 if color[x] == black
    x = left[x]
  end
  count
end
```
