---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: find_pair_indices
fn_javascript: findPairIndices
fn_typescript: findPairIndices
fn_java: findPairIndices
fn_cpp: find_pair_indices
fn_c: find_pair_indices
fn_rust: find_pair_indices
fn_go: findPairIndices
fn_csharp: FindPairIndices
fn_ruby: find_pair_indices
test_cases: [{"args": [[], 5], "expected": []}, {"args": [[4], 4], "expected": []}, {"args": [[3, 3], 6], "expected": [0, 1]}, {"args": [[8, -3, 5, 11, 2, 6], 8], "expected": [1, 3]}, {"args": [[1, 2, 3], 10], "expected": []}, {"args": [[5, 1, 5, 5], 10], "expected": [0, 2]}, {"args": [[-7, 4, 0, -4, 7, 7], 0], "expected": [0, 4]}, {"args": [[9, 6, 6, 1], 12], "expected": [1, 2]}]
---

# Complement Indices — Easy — Arrays and Hashing

## Problem
Given an integer list `values` and an integer `target`, find two positions `i` and `j` with `i < j` such that `values[i] + values[j] == target`. A position may not be used twice, but equal values at different positions are fine. If several pairs qualify, return the one with the smallest `i`; among those, the one with the smallest `j`. Return the pair as `[i, j]`. If no pair qualifies, return an empty list. An empty list or a single element has no pair.

## Example
values = [8,-3,5,11,2,6], target = 8 → [1,3] (the values -3 and 11 at positions 1 and 3 sum to 8; the 8 at position 0 has no partner)

## Approach
Scan from right to left and keep a hash map from each value to the leftmost position seen so far to its right. At position `i`, look up `target - values[i]`; a hit gives a valid pair starting at `i` whose `j` is the smallest possible. Each later hit overwrites the answer, so the final answer is the hit with the smallest `i`. Time O(n), space O(n).

## Hints
- Scanning right to left lets the map keep the leftmost position of each value, which is the smallest valid j.
- Look up the complement before inserting the current value, so a position is never paired with itself.
- Overwrite the answer on every hit; the last hit has the smallest i.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def find_pair_indices(values, target):
    best = []
    later = {}  # value -> leftmost position among those to the right of i
    for i in range(len(values) - 1, -1, -1):
        need = target - values[i]
        if need in later:
            best = [i, later[need]]
        later[values[i]] = i
    return best
```

### JavaScript
```javascript
function findPairIndices(values, target) {
  let best = [];
  const later = new Map();
  for (let i = values.length - 1; i >= 0; i--) {
    const need = target - values[i];
    if (later.has(need)) best = [i, later.get(need)];
    later.set(values[i], i);
  }
  return best;
}
```

### TypeScript
```typescript
function findPairIndices(values: number[], target: number): number[] {
  let best: number[] = [];
  const later = new Map<number, number>();
  for (let i = values.length - 1; i >= 0; i--) {
    const need = target - values[i];
    if (later.has(need)) best = [i, later.get(need)!];
    later.set(values[i], i);
  }
  return best;
}
```

### Java
```java
public long[] findPairIndices(long[] values, long target) {
    long[] best = new long[0];
    Map<Long, Integer> later = new HashMap<>();
    for (int i = values.length - 1; i >= 0; i--) {
        Integer j = later.get(target - values[i]);
        if (j != null) best = new long[]{i, j};
        later.put(values[i], i);
    }
    return best;
}
```

### C++
```cpp
#include <unordered_map>
#include <vector>
std::vector<long long> find_pair_indices(std::vector<long long>& values, long long target) {
    std::vector<long long> best;
    std::unordered_map<long long, long long> later;
    for (long long i = (long long)values.size() - 1; i >= 0; i--) {
        auto it = later.find(target - values[i]);
        if (it != later.end()) best = {i, it->second};
        later[values[i]] = i;
    }
    return best;
}
```

### C
```c
long long* find_pair_indices(long long* values, int valuesSize, long long target, int* returnSize) {
    long long* out = malloc(2 * sizeof(long long));
    *returnSize = 0;
    for (int i = 0; i < valuesSize; i++) {
        for (int j = i + 1; j < valuesSize; j++) {
            if (values[i] + values[j] == target) {
                out[0] = i;
                out[1] = j;
                *returnSize = 2;
                return out;
            }
        }
    }
    return out;
}
```

### Rust
```rust
use std::collections::HashMap;
pub fn find_pair_indices(values: Vec<i64>, target: i64) -> Vec<i64> {
    let mut best: Vec<i64> = vec![];
    let mut later: HashMap<i64, i64> = HashMap::new();
    for i in (0..values.len()).rev() {
        if let Some(&j) = later.get(&(target - values[i])) {
            best = vec![i as i64, j];
        }
        later.insert(values[i], i as i64);
    }
    best
}
```

### Go
```go
func findPairIndices(values []int, target int) []int {
	best := []int{}
	later := make(map[int]int)
	for i := len(values) - 1; i >= 0; i-- {
		if j, ok := later[target-values[i]]; ok {
			best = []int{i, j}
		}
		later[values[i]] = i
	}
	return best
}
```

### C#
```csharp
public static long[] FindPairIndices(long[] values, long target)
{
    long[] best = new long[0];
    var later = new System.Collections.Generic.Dictionary<long, long>();
    for (int i = values.Length - 1; i >= 0; i--)
    {
        if (later.TryGetValue(target - values[i], out long j)) best = new long[] { i, j };
        later[values[i]] = i;
    }
    return best;
}
```

### Ruby
```ruby
def find_pair_indices(values, target)
  best = []
  later = {}
  (values.length - 1).downto(0) do |i|
    best = [i, later[target - values[i]]] if later.key?(target - values[i])
    later[values[i]] = i
  end
  best
end
```
