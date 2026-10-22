---
track: algorithm
difficulty: Hard
algorithms: red-black-tree-concept
category: Data Structure
source: authored
io_mode: function
---
# Red-black trees — Hard — Data Structure

A red-black tree is a binary search tree whose nodes carry one extra bit, red or black. The colour rules stop the tree from degenerating into a list, so lookups, inserts and deletes stay logarithmic.

## Overview
Every node is red or black, and the tree obeys five rules:

1. Every node is red or black.
2. The root is black.
3. Every leaf is a NIL sentinel, and NIL is black.
4. A red node has two black children (no red node has a red child).
5. Every path from a node down to a NIL leaf contains the same number of black nodes.

Rule 5 makes the black count along any path the same, so the black height is well defined. Together with rule 4 it bounds the height: a red-black tree with n internal nodes has height at most 2 log2(n + 1).

## What the structure guarantees
- The height is at most 2 log2(n + 1), even when keys arrive in sorted order (the worst case for a plain BST).
- Search, insert and delete run in O(log n) time.
- An insert needs O(log n) recolouring and at most two rotations. A delete needs at most three rotations.
- An in-order walk still yields the keys in sorted order, because rotations and recolourings never change the key order.

## Operations and complexity
| Operation | Time | Rotations |
| --- | --- | --- |
| Search | O(log n) | none |
| Insert | O(log n) | at most 2 |
| Delete | O(log n) | at most 3 |
| Min, max, in-order walk | O(log n), O(n) for the walk | none |

Insert (CLRS `RB-INSERT`): descend as in a plain BST, attach the new node as a red leaf, then run `RB-INSERT-FIXUP`. If the uncle is red, recolour the parent, uncle and grandparent, and move up to the grandparent. If the uncle is black, rotate once (zig-zag case) or once more (zig-zig case) and stop. Finish by colouring the root black.

## Common mistakes
- Colouring the new node black. A new node is red, which keeps rule 5 intact and only risks rule 4.
- Forgetting to repaint the root black after the fix-up loop. Recolouring can turn the root red.
- Writing into the parent field of the NIL sentinel, or colouring NIL red. Keep NIL black and guard parent updates in rotations.
- Mixing up the left and right mirror cases. Write the left case, then mirror it exactly for the right case.
- Sending an equal key down a different branch than the descent does. Pick one rule (for example, equal keys go right) and use it in both places.
- Counting NIL when you measure the black height. The black height counts the real black nodes on a path.

## Languages

### Python
Python has no built-in balanced tree, and `dict` and `list` are not ordered trees. The core of an implementation is the rotation, which keeps the search order intact while moving a subtree up.

```python
class Node:
    def __init__(self, key, red=True):
        self.key, self.red = key, red
        self.left = self.right = self.parent = None

def rotate_left(root, x):
    y = x.right
    x.right = y.left
    if y.left:
        y.left.parent = x
    y.parent = x.parent
    if x.parent is None:
        root = y
    elif x is x.parent.left:
        x.parent.left = y
    else:
        x.parent.right = y
    y.left = x
    x.parent = y
    return root

if __name__ == "__main__":
    a, b = Node(1), Node(2)
    a.right, b.parent = b, a
    print(rotate_left(a, a).key)
```

### JavaScript
JavaScript has no built-in balanced tree. `Map` and `Set` keep insertion order, not key order, so an ordered map needs a hand-written tree or a sorted array with binary search. The sketch below mirrors the Python rotation.

```javascript
class TreeNode {
  constructor(key, red = true) {
    this.key = key;
    this.red = red;
    this.left = this.right = this.parent = null;
  }
}

function rotateLeft(root, x) {
  const y = x.right;
  x.right = y.left;
  if (y.left) y.left.parent = x;
  y.parent = x.parent;
  if (x.parent === null) root = y;
  else if (x === x.parent.left) x.parent.left = y;
  else x.parent.right = y;
  y.left = x;
  x.parent = y;
  return root;
}

const a = new TreeNode(1), b = new TreeNode(2);
a.right = b;
b.parent = a;
console.log(rotateLeft(a, a).key);
```

### TypeScript
TypeScript adds types to JavaScript and has no balanced tree in its standard library either. A typed `TreeNode` class and the same rotation give the same behaviour. Use the `strict` compiler flag so that the nullable fields are checked.

```typescript
class TreeNode {
  key: number;
  red: boolean;
  left: TreeNode | null = null;
  right: TreeNode | null = null;
  parent: TreeNode | null = null;

  constructor(key: number, red = true) {
    this.key = key;
    this.red = red;
  }
}

function rotateLeft(root: TreeNode | null, x: TreeNode): TreeNode | null {
  const y = x.right!;
  x.right = y.left;
  if (y.left) y.left.parent = x;
  y.parent = x.parent;
  if (x.parent === null) root = y;
  else if (x === x.parent.left) x.parent.left = y;
  else x.parent.right = y;
  y.left = x;
  x.parent = y;
  return root;
}

const a = new TreeNode(1), b = new TreeNode(2);
a.right = b;
b.parent = a;
console.log(rotateLeft(a, a)!.key);
```

### Java
`java.util.TreeMap` is a red-black tree, and `TreeSet` is built on it. It supplies the ordered queries directly: `ceilingKey` returns the smallest key at or above a value and `floorKey` the largest at or below it. Use it rather than writing your own unless the exercise asks for the tree.

```java
import java.util.TreeMap;

public class Demo {
    public static void main(String[] args) {
        TreeMap<Integer, String> m = new TreeMap<>();
        for (int k : new int[]{10, 20, 30, 15}) {
            m.put(k, "v" + k);
        }
        System.out.println(m.ceilingKey(16));
        System.out.println(m.floorKey(16));
        System.out.println(m.firstKey() + " " + m.lastKey());
    }
}
```

### C
C has no balanced tree in its standard library, so a red-black tree is hand-written. The node carries a colour and parent pointer, and the rotation is the building block the insert fix-up calls.

```c
#include <stdio.h>

typedef struct Node {
    int key;
    int red;
    struct Node *left, *right, *parent;
} Node;

Node *rotate_left(Node *root, Node *x) {
    Node *y = x->right;
    x->right = y->left;
    if (y->left) y->left->parent = x;
    y->parent = x->parent;
    if (x->parent == NULL) root = y;
    else if (x == x->parent->left) x->parent->left = y;
    else x->parent->right = y;
    y->left = x;
    x->parent = y;
    return root;
}

int main(void) {
    Node a = {1, 1, NULL, NULL, NULL}, b = {2, 1, NULL, NULL, NULL};
    a.right = &b;
    b.parent = &a;
    printf("%d\n", rotate_left(&a, &a)->key);
    return 0;
}
```

### C++
The C++ standard requires `std::map` and `std::set` to be ordered with logarithmic operations, but it does not name the tree. In libc++, the default on macOS, the map is a red-black tree; `lower_bound` gives the smallest key at or above a value. Reach for `std::map` before writing a tree.

```cpp
#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<int, std::string> m{{10, "a"}, {20, "b"}, {30, "c"}, {15, "d"}};
    std::cout << m.lower_bound(16)->first << "\n";
    std::cout << std::prev(m.upper_bound(16))->first << "\n";
    return 0;
}
```

### Rust
The standard library has no red-black tree. `BTreeMap` is a B-tree, a different balanced structure with many keys per node, and `range` gives the same ordered queries. Use `BTreeMap` for an ordered map in Rust.

```rust
use std::collections::BTreeMap;

fn main() {
    let mut m = BTreeMap::new();
    for k in [10, 20, 30, 15] {
        m.insert(k, ());
    }
    println!("{:?}", m.range(16..).next().map(|(k, _)| k));
    println!("{:?}", m.range(..=16).next_back().map(|(k, _)| k));
}
```

### Go
Go has no balanced tree or ordered map in its standard library. Keep a sorted slice and use `sort.SearchInts` for a lower-bound query, or hand-write a tree. The sketch shows the node type and the rotation.

```go
type rbNode struct {
	key                 int
	red                 bool
	left, right, parent *rbNode
}

// rotateLeft moves x.right into x's place and returns it.
func rotateLeft(x *rbNode) *rbNode {
	y := x.right
	x.right = y.left
	if y.left != nil {
		y.left.parent = x
	}
	y.parent = x.parent
	if x.parent != nil {
		if x == x.parent.left {
			x.parent.left = y
		} else {
			x.parent.right = y
		}
	}
	y.left = x
	x.parent = y
	return y
}
```

### C#
C# provides `SortedSet<T>` and `SortedDictionary<TKey, TValue>`, both balanced binary search trees. `GetViewBetween` returns a view of the keys in a range, and its `Min` is the smallest key at or above the lower bound. Prefer these collections to a hand-written tree.

```csharp
using System.Collections.Generic;

public static class Lesson {
    // Smallest value in the set that is at least x.
    public static int SmallestAtLeast(SortedSet<int> set, int x) =>
        set.GetViewBetween(x, int.MaxValue).Min;
}
```

### Ruby
Ruby has no balanced tree in its core library. `SortedSet` was deprecated and then removed in Ruby 3.0, so a sorted array with a binary search is the usual substitute. The sketch uses a `Struct` as the node and the rotation as the building block.

```ruby
Node = Struct.new(:key, :red, :left, :right, :parent)

def rotate_left(x)
  y = x.right
  x.right = y.left
  y.left.parent = x if y.left
  y.parent = x.parent
  if x.parent
    x == x.parent.left ? (x.parent.left = y) : (x.parent.right = y)
  end
  y.left = x
  x.parent = y
  y
end

a = Node.new(1, false)
b = Node.new(2, true)
a.right = b
b.parent = a
puts rotate_left(a).key
```
