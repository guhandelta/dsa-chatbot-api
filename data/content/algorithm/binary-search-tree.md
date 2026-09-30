---
track: algorithm
difficulty: Easy
algorithms: binary-search-tree
category: Data Structure
source: authored
io_mode: function
---
# Binary search tree — Easy — Data Structure

In a BST every key in the left subtree is smaller than the node and every key in the right subtree is larger, so search, insert and delete follow one root-to-leaf path. Sorted insertions degrade it into a linked list (h = n), which is why libraries use self-balancing trees. Deletion has three cases: a leaf is removed; a node with one child is spliced out; a node with two children takes its in-order successor's key, then the successor is deleted.

#### BST insert and delete — Python

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def bst_insert(root, key):
    if not root:
        return TreeNode(key)
    if key < root.val:
        root.left = bst_insert(root.left, key)
    elif key > root.val:
        root.right = bst_insert(root.right, key)
    return root

def bst_delete(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = bst_delete(root.left, key)
    elif key > root.val:
        root.right = bst_delete(root.right, key)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = bst_delete(root.right, succ.val)
    return root
```
