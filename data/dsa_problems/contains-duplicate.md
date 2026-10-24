---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: arrays, hash-map
fn_python: contains_duplicate
fn_javascript: containsDuplicate
fn_typescript: containsDuplicate
fn_java: containsDuplicate
fn_cpp: contains_duplicate
fn_c: contains_duplicate
fn_rust: contains_duplicate
fn_go: containsDuplicate
fn_csharp: ContainsDuplicate
fn_ruby: contains_duplicate
test_cases: [{"args": [[]], "expected": false}, {"args": [[7]], "expected": false}, {"args": [[5, 5]], "expected": true}, {"args": [[2, 4, 6, 8, 10]], "expected": false}, {"args": [[9, 9, 9, 9]], "expected": true}, {"args": [[-3, 0, -3, 7]], "expected": true}, {"args": [[100, 200, 300, 400, 500, 600, 700]], "expected": false}, {"args": [[2147483647, -2147483648, 0, 2147483647]], "expected": true}]
---
# Detect a Repeated Value — Easy — Array, Hash Set

## Problem
Given a list of integers `items`, return `true` if at least one value occurs two or more times in the list, and `false` if every value is different. An empty list and a one-element list both contain no repeated value. Every value fits in a signed 32-bit integer.

## Example
items = [10,-4,7,10,2] → true

## Approach
Record each value in a hash set as you scan the list. The first time a value is already in the set, you have found a repeat. Time O(n), space O(n). If you are allowed to reorder the list, sorting it first gives O(n log n) time with O(1) extra space.

## Hints
- A set answers "have I seen this value?" in constant time.
- Comparing the number of distinct values with the length of the list also settles the question.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def contains_duplicate(items):
    return len(set(items)) < len(items)
```

### JavaScript
```javascript
function containsDuplicate(items) {
  return new Set(items).size < items.length;
}
```

### TypeScript
```typescript
function containsDuplicate(items: number[]): boolean {
  return new Set(items).size < items.length;
}
```

### Java
```java
public boolean containsDuplicate(int[] items) {
    Set<Integer> seen = new HashSet<>();
    for (int x : items) if (!seen.add(x)) return true;
    return false;
}
```

### C++
```cpp
#include <unordered_set>
#include <vector>
bool contains_duplicate(std::vector<int>& items) {
    std::unordered_set<int> seen;
    for (int x : items) if (!seen.insert(x).second) return true;
    return false;
}
```

### C
```c
static int cmp_int(const void* a, const void* b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}
bool contains_duplicate(int* items, int itemsSize) {
    qsort(items, itemsSize, sizeof(int), cmp_int);   /* O(n log n) time, O(1) extra */
    for (int i = 1; i < itemsSize; i++)
        if (items[i] == items[i - 1]) return true;
    return false;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn contains_duplicate(items: Vec<i32>) -> bool {
    let mut seen = HashSet::new();
    items.into_iter().any(|x| !seen.insert(x))
}
```

### Go
```go
func containsDuplicate(items []int) bool {
	seen := make(map[int]bool)
	for _, x := range items {
		if seen[x] {
			return true
		}
		seen[x] = true
	}
	return false
}
```

### C#
```csharp
public static bool ContainsDuplicate(int[] items)
{
    var seen = new System.Collections.Generic.HashSet<int>();
    foreach (int x in items)
    {
        if (!seen.Add(x)) return true;
    }
    return false;
}
```

### Ruby
```ruby
def contains_duplicate(items)
  items.uniq.length < items.length
end
```
