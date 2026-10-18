---
track: algorithm
difficulty: Medium
algorithms: lowest-common-ancestor
category: Data Structure
source: authored
io_mode: function
---
# Lowest common ancestor (LCA) — Medium — Data Structure

The lowest common ancestor of nodes p and q is the deepest node that has both as descendants, where a node counts as its own descendant. In a general binary tree, recurse: a node is the LCA if p and q are found in different subtrees, or if it is p or q itself and the other lies below it. In a BST, walk from the root: if both keys are smaller go left, if both are larger go right, otherwise the current node splits them and is the LCA. For many queries on a fixed tree, binary lifting stores every node's 2ʲ-th ancestor, lifts the deeper node to the same depth, then lifts both while their ancestors differ. The distance between two nodes is depth\[p\] + depth\[q\] − 2 × depth\[lca\].

#### Lowest common ancestor — Python

```python
def lca_binary_tree(root, p, q):           # p and q are nodes present in the tree
    if root is None or root is p or root is q:
        return root
    left = lca_binary_tree(root.left, p, q)
    right = lca_binary_tree(root.right, p, q)
    return root if left and right else left or right

def lca_bst(root, p, q):
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node
    return None

class BinaryLifting:                        # nodes 0..n-1; parent[root] == root
    def __init__(self, parent, depth):
        n = len(parent)
        self.log = max(1, n.bit_length())
        self.depth = depth
        self.up = [parent[:]]               # up[j][v] = 2^j-th ancestor of v
        for _ in range(1, self.log):
            prev = self.up[-1]
            self.up.append([prev[prev[v]] for v in range(n)])

    def lca(self, a, b):
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        diff = self.depth[a] - self.depth[b]
        for j in range(self.log):
            if (diff >> j) & 1:
                a = self.up[j][a]
        if a == b:
            return a
        for j in range(self.log - 1, -1, -1):
            if self.up[j][a] != self.up[j][b]:
                a, b = self.up[j][a], self.up[j][b]
        return self.up[0][a]
```
