---
track: dsa
difficulty: Hard
source: authored
io_mode: function
algorithms: b-tree
fn_python: btree_height
fn_javascript: btreeHeight
fn_typescript: btreeHeight
fn_java: btreeHeight
fn_cpp: btree_height
fn_c: btree_height
fn_rust: btree_height
fn_go: btreeHeight
fn_csharp: BtreeHeight
fn_ruby: btree_height
test_cases: [{"args": [[], 3], "expected": 0}, {"args": [[7], 3], "expected": 1}, {"args": [[2, 1], 3], "expected": 1}, {"args": [[1, 2, 3], 3], "expected": 2}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3], "expected": 3}, {"args": [[10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130], 4], "expected": 3}, {"args": [[5, -3, 9007199254740991, -9007199254740991, 0, 42], 4], "expected": 2}, {"args": [[8, 3, 14, 1, 9, 27, 5, 11, 2, 40, 7, 19, 30, 4, 16, 22], 5], "expected": 2}]
---
# B-tree Height — Hard — Data Structure

## Problem
Insert the given distinct integers into an initially empty B-tree of the given `order`, one at a time in array order. Return the number of levels in the tree after all insertions.

The tree obeys these rules:
- `order` (an integer, at least 3) is the maximum number of children per node. A node holds at most `order - 1` keys.
- Insert a key into a leaf at its sorted position. All leaves stay at the same depth.
- A node splits as soon as it holds exactly `order` keys (one more than allowed). Let `mid = order // 2`. The keys before index `mid` stay in the left node, key `mid` is the median, and the keys after it move to a new right node. For an internal node, the children after index `mid` move to the right node too, and the left node keeps children `0..mid`.
- The median moves up into the parent, in the position of the split node. The parent may then split in the same way, and so on.
- If the root splits, a new root holding only the median is created with the two halves as children. This is the only way the height grows.

Return the number of levels: `0` for empty input, `1` for a single key (the root is a leaf).

## Example
values = [1, 2, 3], order = 3 → 2

Insert 1 and 2: the root is `[1, 2]`. Inserting 3 gives `[1, 2, 3]`, which reaches `order` keys. With `mid = 1`, the median 2 moves up into a new root, giving `[2]` with children `[1]` and `[3]`. That is 2 levels.

## Approach
Insert recursively. Each call inserts the key into the right child, and if that child reports a split (its median and new right sibling), it adds the median and sibling to the current node. The current node then checks its own size and may split too, returning a new median and sibling to its parent. Only a split at the root changes the height, so track the height as a counter. Time is O(n · h · order) where h is the height, since each insertion scans the keys of about h nodes. Space is O(n).

## Hints
- Check for overflow after inserting into a node, and split only when the key count equals `order`.
- Use `mid = order // 2`. Both halves are non-empty for every `order >= 3`.
- For a leaf, the children lists are empty, so do not slice them as if they had `order` entries.
- Start the height at 1 after the first key, and add 1 only when the root splits.

## Solutions
*Conventions: C# has the helper classes inside `class Solution`. Java helpers are static nested classes inside `class Solution`. C uses `malloc` for nodes and does not free them. Rust is a free function. Integers are 64-bit in every language.*

### Python
```python
class BNode:
    def __init__(self, keys=None, children=None):
        self.keys = keys if keys is not None else []
        self.children = children if children is not None else []

def _insert(node, key, order):
    i = sum(1 for k in node.keys if k < key)
    if node.children:
        promoted = _insert(node.children[i], key, order)
        if promoted is not None:
            median, right = promoted
            node.keys.insert(i, median)
            node.children.insert(i + 1, right)
    else:
        node.keys.insert(i, key)
    if len(node.keys) == order:
        mid = order // 2
        median = node.keys[mid]
        right = BNode(node.keys[mid + 1:], node.children[mid + 1:])
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return median, right
    return None

def btree_height(values, order):
    if not values:
        return 0
    root = BNode()
    height = 1
    for v in values:
        promoted = _insert(root, v, order)
        if promoted is not None:
            median, right = promoted
            root = BNode([median], [root, right])
            height += 1
    return height
```

### JavaScript
```javascript
class BNode {
  constructor(keys = [], children = []) {
    this.keys = keys;
    this.children = children;
  }
}

function insertInto(node, key, order) {
  let i = 0;
  while (i < node.keys.length && node.keys[i] < key) i++;
  if (node.children.length > 0) {
    const promoted = insertInto(node.children[i], key, order);
    if (promoted !== null) {
      node.keys.splice(i, 0, promoted.median);
      node.children.splice(i + 1, 0, promoted.right);
    }
  } else {
    node.keys.splice(i, 0, key);
  }
  if (node.keys.length === order) {
    const mid = Math.floor(order / 2);
    const median = node.keys[mid];
    const right = new BNode(node.keys.slice(mid + 1), node.children.slice(mid + 1));
    node.keys = node.keys.slice(0, mid);
    node.children = node.children.slice(0, mid + 1);
    return { median, right };
  }
  return null;
}

function btreeHeight(values, order) {
  if (values.length === 0) return 0;
  let root = new BNode();
  let height = 1;
  for (const v of values) {
    const promoted = insertInto(root, v, order);
    if (promoted !== null) {
      root = new BNode([promoted.median], [root, promoted.right]);
      height++;
    }
  }
  return height;
}
```

### TypeScript
```typescript
class BNode {
  keys: number[];
  children: BNode[];
  constructor(keys: number[] = [], children: BNode[] = []) {
    this.keys = keys;
    this.children = children;
  }
}

interface Split {
  median: number;
  right: BNode;
}

function insertInto(node: BNode, key: number, order: number): Split | null {
  let i = 0;
  while (i < node.keys.length && node.keys[i] < key) i++;
  if (node.children.length > 0) {
    const promoted = insertInto(node.children[i], key, order);
    if (promoted !== null) {
      node.keys.splice(i, 0, promoted.median);
      node.children.splice(i + 1, 0, promoted.right);
    }
  } else {
    node.keys.splice(i, 0, key);
  }
  if (node.keys.length === order) {
    const mid = Math.floor(order / 2);
    const median = node.keys[mid];
    const right = new BNode(node.keys.slice(mid + 1), node.children.slice(mid + 1));
    node.keys = node.keys.slice(0, mid);
    node.children = node.children.slice(0, mid + 1);
    return { median, right };
  }
  return null;
}

function btreeHeight(values: number[], order: number): number {
  if (values.length === 0) return 0;
  let root = new BNode();
  let height = 1;
  for (const v of values) {
    const promoted = insertInto(root, v, order);
    if (promoted !== null) {
      root = new BNode([promoted.median], [root, promoted.right]);
      height++;
    }
  }
  return height;
}
```

### Java
```java
import java.util.*;

class Solution {
    static class BNode {
        List<Long> keys = new ArrayList<>();
        List<BNode> children = new ArrayList<>();
    }

    static class Split {
        final long median;
        final BNode right;
        Split(long median, BNode right) { this.median = median; this.right = right; }
    }

    static Split insertInto(BNode node, long key, int order) {
        int i = 0;
        while (i < node.keys.size() && node.keys.get(i) < key) i++;
        if (!node.children.isEmpty()) {
            Split promoted = insertInto(node.children.get(i), key, order);
            if (promoted != null) {
                node.keys.add(i, promoted.median);
                node.children.add(i + 1, promoted.right);
            }
        } else {
            node.keys.add(i, key);
        }
        if (node.keys.size() == order) {
            int mid = order / 2;
            long median = node.keys.get(mid);
            BNode right = new BNode();
            right.keys.addAll(node.keys.subList(mid + 1, node.keys.size()));
            node.keys = new ArrayList<>(node.keys.subList(0, mid));
            if (!node.children.isEmpty()) {
                right.children.addAll(node.children.subList(mid + 1, node.children.size()));
                node.children = new ArrayList<>(node.children.subList(0, mid + 1));
            }
            return new Split(median, right);
        }
        return null;
    }

    public long btreeHeight(long[] values, long order) {
        if (values.length == 0) return 0;
        int m = (int) order;
        BNode root = new BNode();
        long height = 1;
        for (long v : values) {
            Split promoted = insertInto(root, v, m);
            if (promoted != null) {
                BNode newRoot = new BNode();
                newRoot.keys.add(promoted.median);
                newRoot.children.add(root);
                newRoot.children.add(promoted.right);
                root = newRoot;
                height++;
            }
        }
        return height;
    }
}
```

### C++
```cpp
#include <iterator>
#include <utility>
#include <vector>

struct BNode {
    std::vector<long long> keys;
    std::vector<BNode> children;  // empty for a leaf
};

// Returns true when `node` split. Then `median` and `right` hold the promoted key and new sibling.
static bool insert_into(BNode& node, long long key, long long order, long long& median, BNode& right) {
    std::size_t i = 0;
    while (i < node.keys.size() && node.keys[i] < key) ++i;
    if (!node.children.empty()) {
        long long child_median;
        BNode child_right;
        if (insert_into(node.children[i], key, order, child_median, child_right)) {
            node.keys.insert(node.keys.begin() + i, child_median);
            node.children.insert(node.children.begin() + i + 1, std::move(child_right));
        }
    } else {
        node.keys.insert(node.keys.begin() + i, key);
    }
    if (static_cast<long long>(node.keys.size()) == order) {
        std::size_t mid = static_cast<std::size_t>(order / 2);
        median = node.keys[mid];
        right.keys.assign(node.keys.begin() + mid + 1, node.keys.end());
        if (!node.children.empty()) {
            right.children.assign(std::make_move_iterator(node.children.begin() + mid + 1),
                                  std::make_move_iterator(node.children.end()));
            node.children.resize(mid + 1);
        }
        node.keys.resize(mid);
        return true;
    }
    return false;
}

long long btree_height(std::vector<long long>& values, long long order) {
    if (values.empty()) return 0;
    BNode root;
    long long height = 1;
    for (long long v : values) {
        long long median;
        BNode right;
        if (insert_into(root, v, order, median, right)) {
            BNode new_root;
            new_root.keys.push_back(median);
            new_root.children.push_back(std::move(root));
            new_root.children.push_back(std::move(right));
            root = std::move(new_root);
            ++height;
        }
    }
    return height;
}
```

### C
```c
#include <stdlib.h>

typedef struct BNode {
    long long *keys;          /* room for `order` keys */
    struct BNode **children;  /* room for `order + 1` children */
    int nkeys;
    int nchildren;            /* 0 for a leaf */
} BNode;

static BNode *bt_new(long long order) {
    BNode *n = malloc(sizeof *n);
    n->keys = malloc(sizeof(long long) * (order + 1));
    n->children = malloc(sizeof(BNode *) * (order + 2));
    n->nkeys = 0;
    n->nchildren = 0;
    return n;
}

/* Returns 1 when `node` split; *median and *right then hold the promoted key and new sibling. */
static int bt_insert(BNode *node, long long key, long long order, long long *median, BNode **right) {
    int i = 0;
    while (i < node->nkeys && node->keys[i] < key) i++;
    if (node->nchildren > 0) {
        long long child_median;
        BNode *child_right;
        if (bt_insert(node->children[i], key, order, &child_median, &child_right)) {
            for (int j = node->nkeys; j > i; j--) node->keys[j] = node->keys[j - 1];
            node->keys[i] = child_median;
            node->nkeys++;
            for (int j = node->nchildren; j > i + 1; j--) node->children[j] = node->children[j - 1];
            node->children[i + 1] = child_right;
            node->nchildren++;
        }
    } else {
        for (int j = node->nkeys; j > i; j--) node->keys[j] = node->keys[j - 1];
        node->keys[i] = key;
        node->nkeys++;
    }
    if (node->nkeys == order) {
        int mid = (int)(order / 2);
        BNode *r = bt_new(order);
        *median = node->keys[mid];
        for (int j = mid + 1; j < node->nkeys; j++) r->keys[r->nkeys++] = node->keys[j];
        if (node->nchildren > 0) {
            for (int j = mid + 1; j < node->nchildren; j++) r->children[r->nchildren++] = node->children[j];
            node->nchildren = mid + 1;
        }
        node->nkeys = mid;
        *right = r;
        return 1;
    }
    return 0;
}

long long btree_height(long long *values, int valuesSize, long long order) {
    if (valuesSize == 0) return 0;
    BNode *root = bt_new(order);
    long long height = 1;
    for (int v = 0; v < valuesSize; v++) {
        long long median;
        BNode *right;
        if (bt_insert(root, values[v], order, &median, &right)) {
            BNode *new_root = bt_new(order);
            new_root->keys[0] = median;
            new_root->nkeys = 1;
            new_root->children[0] = root;
            new_root->children[1] = right;
            new_root->nchildren = 2;
            root = new_root;
            height++;
        }
    }
    return height;
}
```

### Rust
```rust
struct BNode {
    keys: Vec<i64>,
    children: Vec<BNode>, // empty for a leaf
}

// Returns Some((median, right)) when `node` split.
fn insert_into(node: &mut BNode, key: i64, order: usize) -> Option<(i64, BNode)> {
    let mut i = 0;
    while i < node.keys.len() && node.keys[i] < key {
        i += 1;
    }
    if !node.children.is_empty() {
        if let Some((median, right)) = insert_into(&mut node.children[i], key, order) {
            node.keys.insert(i, median);
            node.children.insert(i + 1, right);
        }
    } else {
        node.keys.insert(i, key);
    }
    if node.keys.len() == order {
        let mid = order / 2;
        let mut right_keys = node.keys.split_off(mid);
        let median = right_keys.remove(0);
        let right_children = if node.children.is_empty() {
            Vec::new()
        } else {
            node.children.split_off(mid + 1)
        };
        return Some((median, BNode { keys: right_keys, children: right_children }));
    }
    None
}

pub fn btree_height(values: Vec<i64>, order: i64) -> i64 {
    if values.is_empty() {
        return 0;
    }
    let order = order as usize;
    let mut root = BNode { keys: Vec::new(), children: Vec::new() };
    let mut height = 1;
    for v in values {
        if let Some((median, right)) = insert_into(&mut root, v, order) {
            root = BNode { keys: vec![median], children: vec![root, right] };
            height += 1;
        }
    }
    height
}
```

### Go
```go
type bNode struct {
	keys     []int64
	children []*bNode // empty for a leaf
}

func insertAt[T any](s []T, i int, v T) []T {
	s = append(s, v)
	copy(s[i+1:], s[i:])
	s[i] = v
	return s
}

// Returns (median, right, true) when node split.
func insertInto(node *bNode, key int64, order int) (int64, *bNode, bool) {
	i := 0
	for i < len(node.keys) && node.keys[i] < key {
		i++
	}
	if len(node.children) > 0 {
		if median, right, ok := insertInto(node.children[i], key, order); ok {
			node.keys = insertAt(node.keys, i, median)
			node.children = insertAt(node.children, i+1, right)
		}
	} else {
		node.keys = insertAt(node.keys, i, key)
	}
	if len(node.keys) == order {
		mid := order / 2
		median := node.keys[mid]
		right := &bNode{keys: append([]int64(nil), node.keys[mid+1:]...)}
		if len(node.children) > 0 {
			right.children = append([]*bNode(nil), node.children[mid+1:]...)
			node.children = node.children[:mid+1]
		}
		node.keys = node.keys[:mid]
		return median, right, true
	}
	return 0, nil, false
}

func btreeHeight(values []int64, order int64) int64 {
	if len(values) == 0 {
		return 0
	}
	m := int(order)
	root := &bNode{}
	var height int64 = 1
	for _, v := range values {
		if median, right, ok := insertInto(root, v, m); ok {
			root = &bNode{keys: []int64{median}, children: []*bNode{root, right}}
			height++
		}
	}
	return height
}
```

### C#
```csharp
public static class Solution {
    class BNode {
        public List<long> Keys = new List<long>();
        public List<BNode> Children = new List<BNode>();
    }

    // Returns true when node split; median and right then hold the promoted key and sibling.
    static bool InsertInto(BNode node, long key, int order, out long median, out BNode right) {
        median = 0;
        right = null;
        int i = 0;
        while (i < node.Keys.Count && node.Keys[i] < key) i++;
        if (node.Children.Count > 0) {
            if (InsertInto(node.Children[i], key, order, out long childMedian, out BNode childRight)) {
                node.Keys.Insert(i, childMedian);
                node.Children.Insert(i + 1, childRight);
            }
        } else {
            node.Keys.Insert(i, key);
        }
        if (node.Keys.Count == order) {
            int mid = order / 2;
            median = node.Keys[mid];
            right = new BNode();
            right.Keys.AddRange(node.Keys.GetRange(mid + 1, node.Keys.Count - mid - 1));
            node.Keys.RemoveRange(mid, node.Keys.Count - mid);
            if (node.Children.Count > 0) {
                right.Children.AddRange(node.Children.GetRange(mid + 1, node.Children.Count - mid - 1));
                node.Children.RemoveRange(mid + 1, node.Children.Count - mid - 1);
            }
            return true;
        }
        return false;
    }

    public static long BtreeHeight(long[] values, long order) {
        if (values.Length == 0) return 0;
        int m = (int)order;
        BNode root = new BNode();
        long height = 1;
        foreach (long v in values) {
            if (InsertInto(root, v, m, out long median, out BNode right)) {
                BNode newRoot = new BNode();
                newRoot.Keys.Add(median);
                newRoot.Children.Add(root);
                newRoot.Children.Add(right);
                root = newRoot;
                height++;
            }
        }
        return height;
    }
}
```

### Ruby
```ruby
class BNode
  attr_accessor :keys, :children

  def initialize(keys = [], children = [])
    @keys = keys
    @children = children
  end
end

# Returns [median, right] when node split, otherwise nil.
def bt_insert(node, key, order)
  i = node.keys.count { |k| k < key }
  if node.children.empty?
    node.keys.insert(i, key)
  else
    promoted = bt_insert(node.children[i], key, order)
    unless promoted.nil?
      node.keys.insert(i, promoted[0])
      node.children.insert(i + 1, promoted[1])
    end
  end
  return nil unless node.keys.length == order
  mid = order / 2
  median = node.keys[mid]
  right_children = node.children.empty? ? [] : node.children[(mid + 1)..-1]
  right = BNode.new(node.keys[(mid + 1)..-1], right_children)
  node.keys = node.keys[0...mid]
  node.children = node.children[0..mid] unless node.children.empty?
  [median, right]
end

def btree_height(values, order)
  return 0 if values.empty?
  root = BNode.new
  height = 1
  values.each do |v|
    promoted = bt_insert(root, v, order)
    unless promoted.nil?
      root = BNode.new([promoted[0]], [root, promoted[1]])
      height += 1
    end
  end
  height
end
```
