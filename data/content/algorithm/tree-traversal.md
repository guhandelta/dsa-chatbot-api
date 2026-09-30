---
track: algorithm
difficulty: Easy
algorithms: tree-traversal
category: Data Structure
source: authored
io_mode: function
---
# Binary tree traversals — Easy — Data Structure

A binary tree node has at most two children. Traversal order decides what each problem can compute; h is tree height and w is maximum level width.

| Order | Visit sequence | Typical use |
| --- | --- | --- |
| Pre-order | Node, left, right | Copy or serialise a tree, print a directory |
| In-order | Left, node, right | Sorted output from a BST, validate a BST |
| Post-order | Left, right, node | Delete a tree, compute heights, evaluate expression trees |
| Level-order | Breadth-first, level by level | Minimum depth, right-side view, zigzag order |

#### Iterative in-order and level-order traversal — Python

```python
from collections import deque

def inorder(root):                     # iterative: no recursion-depth limit
    out, st, node = [], [], root
    while st or node:
        while node:
            st.append(node); node = node.left
        node = st.pop()
        out.append(node.val)
        node = node.right
    return out

def level_order(root):
    if not root:
        return []
    res, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft(); level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        res.append(level)
    return res
```
