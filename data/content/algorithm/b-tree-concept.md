---
track: algorithm
difficulty: Hard
algorithms: b-tree-concept
category: Data Structure
source: authored
io_mode: function
---
# B-trees — Hard — Data Structure

A B-tree is a search tree whose nodes hold many sorted keys instead of one. Wide nodes keep the tree shallow, so a lookup touches few nodes, which suits disk pages, database indexes and filesystems. Every leaf sits at the same depth, and the tree grows at the top: a root that overflows splits and adds one level, instead of the tree growing unevenly at the bottom.

## What the structure guarantees
With a parameter `order` (the maximum number of children per node), a node holds at most `order - 1` keys. The tree stays balanced under any insertion order because of the split rule below:

- A node that reaches `order` keys splits. With `mid = order // 2`, the key at `mid` moves up to the parent, and the keys and children to its left and right form two nodes.
- Splits propagate upward. Only a root split adds a level.
- Each split leaves both halves with at least `ceil(order / 2) - 1` keys, so the tree is never sparse. Insert-only trees need no further rules; deletion has its own rebalancing.

This lesson uses the split-on-overflow rule. A different variant (CLRS-style) splits full nodes on the way down, so the same input can produce a different shape. Check which rule a problem uses before comparing results.

## Operations and complexity
| Operation | Cost with order `m` and `n` keys |
| --- | --- |
| Search | O(log n) node reads when `m` is fixed; O(m) key scan per node (O(log m) with binary search) |
| Insert | O(log n) node reads down, plus at most one split per level up; O(m) per node touched |
| Height | O(log n) levels; height grows only when the root splits |
| Space | O(n) keys |

## Common mistakes
- Splitting at the wrong size. A node holds `order - 1` keys after insertion; the split fires when it reaches `order`, not earlier.
- Keeping the median in a child. The median moves up to the parent, and the two halves do not contain it.
- Treating it like a binary search tree. Nodes have many children and a child's keys lie between two adjacent keys of its parent.
- Slicing an empty children list as if it had `order` entries. Leaves have no children.
- Forgetting the root. When the root splits, a new root is created and the height increases by one; no other split changes the height.

## Languages

### Python
Python's standard library has no balanced tree or B-tree. The `bisect` module finds positions in a sorted list, but it does not balance anything, so a B-tree is hand-written. Slicing gives the two halves of a split directly.

```python
keys = [1, 2, 3]              # a node that reached order = 3 keys
mid = 3 // 2
left, median, right = keys[:mid], keys[mid], keys[mid + 1:]
print(left, median, right)    # [1] 2 [3]
```

### JavaScript
JavaScript has no built-in ordered map or tree, so a B-tree is hand-written with arrays. `slice` produces each half without mutating the original, and `splice` inserts a median into a parent at a given position.

```javascript
const keys = [1, 2, 3];       // a node that reached order = 3 keys
const mid = Math.floor(3 / 2);
const left = keys.slice(0, mid), median = keys[mid], right = keys.slice(mid + 1);
console.log(JSON.stringify([left, median, right])); // [[1],2,[3]]
```

### TypeScript
TypeScript has no built-in B-tree; it compiles to the same hand-written JavaScript structure. Types document the node shape: keys and children are arrays, and a split returns the median plus a new right node.

```typescript
interface Split { median: number; right: number[] }

const keys: number[] = [1, 2, 3];   // a node that reached order = 3 keys
const mid = Math.floor(3 / 2);
const split: Split = { median: keys[mid], right: keys.slice(mid + 1) };
console.log(JSON.stringify([keys.slice(0, mid), split.median, split.right])); // [[1],2,[3]]
```

### Java
Java's `TreeMap` is a red-black tree, not a B-tree, and it does not expose node structure or height. Use `TreeMap` for ordered maps; for a B-tree, the node split is hand-written. `List.subList` gives the two halves of a split as views, copied here so the parent keeps its own list.

```java
import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<Integer> keys = new ArrayList<>(List.of(1, 2, 3)); // order = 3
        int mid = 3 / 2;
        List<Integer> left = new ArrayList<>(keys.subList(0, mid));
        int median = keys.get(mid);
        List<Integer> right = new ArrayList<>(keys.subList(mid + 1, keys.size()));
        System.out.println(left + " " + median + " " + right); // [1] 2 [3]
    }
}
```

### C++
`std::map` and `std::set` are red-black trees in mainstream standard libraries, so they are not B-trees. A B-tree node is a `std::vector` of keys and a `std::vector` of child nodes, and a split moves a range of each with `assign`.

```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<long long> keys = {1, 2, 3};   // order = 3
    std::size_t mid = 3 / 2;
    std::vector<long long> left(keys.begin(), keys.begin() + mid);
    long long median = keys[mid];
    std::vector<long long> right(keys.begin() + mid + 1, keys.end());
    std::cout << left.size() << " " << median << " " << right.size() << "\n"; // 1 2 1
}
```

### C
C has no containers, so a B-tree node is a struct with fixed-size arrays or `malloc`'d storage. A split copies the upper half of the keys into a new node and shortens the original. The code below shows only the split on a plain array.

```c
#include <stdio.h>

int main(void) {
    long long keys[] = {1, 2, 3};   /* a node that reached order = 3 keys */
    int order = 3, mid = order / 2;
    long long median = keys[mid];
    int right_count = order - mid - 1;
    printf("%d %lld %d\n", mid, median, right_count); /* 1 2 1 */
    return 0;
}
```

### Rust
Rust's `BTreeMap` is a real B-tree in the standard library, and it gives ordered iteration and range queries. Its node size and height are not exposed, so this exercise needs a hand-written tree that tracks its own levels. `range` answers "smallest key at least x" directly.

```rust
use std::collections::BTreeMap;

fn main() {
    let mut m = BTreeMap::new();
    for k in [3, 1, 2] {
        m.insert(k, ());
    }
    let keys: Vec<_> = m.keys().copied().collect();
    println!("{:?}", keys);                // [1, 2, 3]
    println!("{:?}", m.range(2..).next()); // Some((2, ()))
}
```

### Go
Go has no built-in ordered map or tree. A B-tree node is a struct with a slice of keys and a slice of child pointers, and a split copies the upper part of each slice into a new node.

```go
package main

import "fmt"

func main() {
	keys := []int{1, 2, 3} // a node that reached order = 3 keys
	mid := 3 / 2
	left := append([]int(nil), keys[:mid]...)
	median := keys[mid]
	right := append([]int(nil), keys[mid+1:]...)
	fmt.Println(left, median, right) // [1] 2 [3]
}
```

### C#
`SortedSet<T>` and `SortedDictionary<TKey, TValue>` are red-black trees, so they are not B-trees. A B-tree in C# is hand-written with `List<T>`, and `GetRange` and `RemoveRange` perform a split.

```csharp
using System;
using System.Collections.Generic;

class Program {
    static void Main() {
        var keys = new List<long> { 1, 2, 3 }; // order = 3
        int mid = 3 / 2;
        long median = keys[mid];
        var left = keys.GetRange(0, mid);
        var right = keys.GetRange(mid + 1, keys.Count - mid - 1);
        Console.WriteLine($"{left.Count} {median} {right.Count}"); // 1 2 1
    }
}
```

### Ruby
Ruby has no built-in ordered map or tree. Arrays provide the split directly: a range slice gives the upper keys, and `[0...mid]` keeps the lower ones. Ruby has no B-tree in its standard library.

```ruby
keys = [1, 2, 3]   # a node that reached order = 3 keys
mid = 3 / 2
left = keys[0...mid]
median = keys[mid]
right = keys[(mid + 1)..-1]
p [left, median, right]   # [[1], 2, [3]]
```
