---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: has_repeat
fn_javascript: hasRepeat
fn_typescript: hasRepeat
fn_java: hasRepeat
fn_cpp: has_repeat
fn_c: has_repeat
fn_rust: has_repeat
fn_go: hasRepeat
fn_csharp: HasRepeat
fn_ruby: has_repeat
test_cases: [{"args": [[]], "expected": false}, {"args": [[5]], "expected": false}, {"args": [[7, 4, 9, 4, 1]], "expected": true}, {"args": [[0, 0]], "expected": true}, {"args": [[2, -2, 3, -3]], "expected": false}, {"args": [[10, 20, 30, 40, 50, 60, 10]], "expected": true}, {"args": [[-1, -2, -3, -4]], "expected": false}, {"args": [[100, 200, 300, 400, 500, 600, 700, 800, 900, 100]], "expected": true}]
---

# Duplicate Presence — Easy — Arrays and Hashing

## Problem
Given `values`, a list of integers that may be empty, return `true` if at least one integer appears two or more times in the list, and `false` if every integer in it is different from all the others. Negative numbers are allowed. An empty list or a one-element list returns `false`.

## Example
values = [7,4,9,4,1] → true (the value 4 appears twice)

## Approach
Walk the list while remembering every value already seen in a hash set. The first value that is already in the set is a repeat, so return `true` at once. If the walk finishes without a hit, every value is distinct and the answer is `false`. Time O(n), space O(n).

## Hints
- A hash set answers "have I seen this value?" in O(1) on average.
- You can stop at the first repeat; you never need to count occurrences.
- Comparing the set's size with the list's length is an equivalent one-line check.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def has_repeat(values):
    seen = set()
    for v in values:
        if v in seen:
            return True
        seen.add(v)
    return False
```

### JavaScript
```javascript
function hasRepeat(values) {
  const seen = new Set();
  for (const v of values) {
    if (seen.has(v)) return true;
    seen.add(v);
  }
  return false;
}
```

### TypeScript
```typescript
function hasRepeat(values: number[]): boolean {
  const seen = new Set<number>();
  for (const v of values) {
    if (seen.has(v)) return true;
    seen.add(v);
  }
  return false;
}
```

### Java
```java
public boolean hasRepeat(long[] values) {
    Set<Long> seen = new HashSet<>();
    for (long v : values) {
        if (!seen.add(v)) return true;
    }
    return false;
}
```

### C++
```cpp
#include <unordered_set>
#include <vector>
bool has_repeat(std::vector<long long>& values) {
    std::unordered_set<long long> seen;
    for (long long v : values) {
        if (!seen.insert(v).second) return true;
    }
    return false;
}
```

### C
```c
static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);
}
bool has_repeat(long long* values, int valuesSize) {
    if (valuesSize < 2) return false;
    long long* copy = malloc(valuesSize * sizeof(long long));
    memcpy(copy, values, valuesSize * sizeof(long long));
    qsort(copy, valuesSize, sizeof(long long), cmp_ll);
    bool found = false;
    for (int i = 1; i < valuesSize && !found; i++)
        if (copy[i] == copy[i - 1]) found = true;
    free(copy);
    return found;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn has_repeat(values: Vec<i64>) -> bool {
    let mut seen = HashSet::new();
    for v in values {
        if !seen.insert(v) {
            return true;
        }
    }
    false
}
```

### Go
```go
func hasRepeat(values []int) bool {
	seen := make(map[int]bool)
	for _, v := range values {
		if seen[v] {
			return true
		}
		seen[v] = true
	}
	return false
}
```

### C#
```csharp
public static bool HasRepeat(long[] values)
{
    var seen = new System.Collections.Generic.HashSet<long>();
    foreach (long v in values)
    {
        if (!seen.Add(v)) return true;
    }
    return false;
}
```

### Ruby
```ruby
def has_repeat(values)
  seen = {}
  values.each do |v|
    return true if seen.key?(v)
    seen[v] = true
  end
  false
end
```
