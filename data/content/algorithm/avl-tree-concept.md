---
track: algorithm
difficulty: Medium
algorithms: avl-tree-concept
category: Data Structure
source: authored
io_mode: function
---
# AVL trees — Medium — Data Structure

An AVL tree is a binary search tree that rebalances itself after every insertion or deletion, so its height stays O(log n) no matter what order the keys arrive in. It is the oldest self-balancing tree and is stricter than a red-black tree, so lookups are a little faster at the cost of more rotations on writes.

## What the structure guarantees
- Ordering: every key in a left subtree is smaller than the node's key, and every key in a right subtree is larger (as in any BST).
- Balance: for every node, the heights of its left and right subtrees differ by at most 1. The difference is the node's balance factor, and it is always -1, 0 or +1.
- Height: at most about 1.44·log2(n + 2). A tree with n nodes is never much taller than a perfectly balanced one.

Each node stores its height (or balance factor), so a rebalance check costs O(1) per node on the path back to the root.

## Operations
| Operation | Time | Notes |
| --- | --- | --- |
| Search | O(log n) | Same walk as a plain BST, guaranteed short |
| Insert | O(log n) | At most two rotations (one single or one double) restore balance |
| Delete | O(log n) | Can need a rotation at every node on the path back up |
| Rotation | O(1) | Single left, single right, or a double rotation built from two singles |

**The four insertion cases.** After inserting, walk up from the new leaf. At the first node whose balance factor becomes +2 or -2, the new key's position decides the fix:
- Left-left: rotate right at the unbalanced node.
- Right-right: rotate left at the unbalanced node.
- Left-right: rotate left at the left child, then rotate right at the unbalanced node.
- Right-left: rotate right at the right child, then rotate left at the unbalanced node.

Only one rebalance step is needed per insertion, which is why insertion does at most two rotations.

## Common mistakes
- Updating the height of the node that moves to the top of a rotation before the node that moves down. The lower node must be recomputed first.
- Choosing the double-rotation case from the child's balance factor instead of the inserted key's position. For a left-heavy child, the key is either in its left subtree (single rotation) or its right subtree (double rotation).
- Forgetting to recompute heights on the way back up, so later balance factors read stale values.
- Treating a duplicate key as a new node. Decide the policy (ignore, or count) and apply it consistently.
- Assuming the tree is balanced after a single rotation in a deep case. Rotations are local; check the balance at each node on the way up.

## Languages

### Python
Python's standard library has no balanced search tree. `bisect` keeps a sorted list with O(n) inserts, and `heapq` is a heap, not an ordered map. An AVL tree is written by hand, with a small node class and the rotations as functions.
```python
def _rot_r(y):
    x = y.l
    y.l = x.r
    x.r = y
    _upd(y)
    _upd(x)
    return x
```

### JavaScript
JavaScript has `Map` and `Set`, which are hash-based and do not keep keys in order. There is no built-in ordered tree, so an AVL tree is a hand-written object-based node with the same rotation helpers.
```javascript
function avlRotR(y) {
  const x = y.l;
  y.l = x.r;
  x.r = y;
  avlUpd(y);
  avlUpd(x);
  return x;
}
```

### TypeScript
TypeScript adds no runtime collection, so the tree is the same as JavaScript. The node type is an interface, and nullable children are typed as `AvlNode | null`, which keeps the rotation code honest about missing children.
```typescript
interface AvlNode {
  v: number;
  l: AvlNode | null;
  r: AvlNode | null;
  h: number;
}
```

### Java
`java.util.TreeMap` and `TreeSet` are ordered and balanced, but they are red-black trees, not AVL trees. Use them when you need an ordered map (`ceilingKey`, `floorKey`, `firstKey`). When the AVL property itself is the point, write the tree by hand, as the exercise solution does.
```java
static AvlNode avlRotR(AvlNode y) {
    AvlNode x = y.l;
    y.l = x.r;
    x.r = y;
    avlUpd(y);
    avlUpd(x);
    return x;
}
```

### C
C has no standard container of any kind, so a balanced tree is hand-written with `malloc` and `free`. Keep the height in each node and free the whole tree at the end, since the library does not do it for you.
```c
static AvlNode *avl_rot_r(AvlNode *y) {
    AvlNode *x = y->l;
    y->l = x->r;
    x->r = y;
    avl_upd(y);
    avl_upd(x);
    return x;
}
```

### C++
`std::map` and `std::set` give O(log n) ordered operations, and the standard does not say which balancing algorithm to use. Common implementations use red-black trees. For a guaranteed AVL tree, write a node with `new` and `delete`, and free the tree explicitly.
```cpp
static AvlNode* avl_rot_r(AvlNode* y) {
    AvlNode* x = y->l;
    y->l = x->r;
    x->r = y;
    avl_upd(y);
    avl_upd(x);
    return x;
}
```

### Rust
`BTreeMap` and `BTreeSet` are ordered, but they are B-trees, not AVL trees. For an AVL tree, use `Option<Box<Node>>` for the children. The `take()` method moves a child out so the rotation can reassign it safely without a borrow conflict.
```rust
fn avl_rot_r(mut y: Box<AvlNode>) -> Box<AvlNode> {
    let mut x = y.l.take().unwrap();
    y.l = x.r.take();
    avl_upd(&mut y);
    x.r = Some(y);
    avl_upd(&mut x);
    x
}
```

### Go
Go has no ordered map or balanced tree in its standard library (maps are unordered, and `sort` works on slices). An AVL tree is written with a pointer-based node struct, and the rotations return the new subtree root.
```go
func avlRotR(y *avlNode) *avlNode {
	x := y.l
	y.l = x.r
	x.r = y
	avlUpd(y)
	avlUpd(x)
	return x
}
```

### C#
`SortedSet<T>` and `SortedDictionary<TKey, TValue>` are ordered, self-balancing collections in .NET, but they are not AVL trees. For an AVL tree, use a nested node class with nullable child references and return the new subtree root from each rotation.
```csharp
private static AvlNode RotR(AvlNode y) {
    AvlNode x = y.L!;
    y.L = x.R;
    x.R = y;
    Upd(y);
    Upd(x);
    return x;
}
```

### Ruby
Ruby has `Hash` and `Array`, but no ordered balanced tree in its standard library. A `Struct` is a convenient node type, and the rotations are plain methods that return the new subtree root.
```ruby
def avl_rot_r(y)
  x = y.l
  y.l = x.r
  x.r = y
  avl_upd(y)
  avl_upd(x)
  x
end
```
