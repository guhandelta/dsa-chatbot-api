---
track: dsa
difficulty: Easy
source: authored
io_mode: function
comparison: unordered_flat
algorithms: arrays, hash-map
fn_python: two_sum
fn_javascript: twoSum
fn_typescript: twoSum
fn_java: twoSum
fn_cpp: two_sum
fn_c: two_sum
fn_rust: two_sum
fn_go: twoSum
fn_csharp: TwoSum
fn_ruby: two_sum
test_cases: [{"args": [[2, 9], 11], "expected": [0, 1]}, {"args": [[4, 4], 8], "expected": [0, 1]}, {"args": [[7, -3, 9, 0], 6], "expected": [1, 2]}, {"args": [[0, 0, 5, 9], 0], "expected": [0, 1]}, {"args": [[-5, -8, 3, 12, -1], -9], "expected": [1, 4]}, {"args": [[2147483647, -2147483648, 1, 0], -1], "expected": [0, 1]}, {"args": [[3, 1, 3, 2], 6], "expected": [0, 2]}, {"args": [[9, 8, 7, 6, 5], 17], "expected": [0, 1]}]
---
# Find a Pair That Sums to a Target — Easy — Array, Hash Map

## Problem
You are given a list of integers `values` and an integer `goal`. Find two different positions i and j in the list whose entries add up to `goal`. Return them as a two-element list `[i, j]` with `i < j`. The input is guaranteed to contain exactly one such pair of positions. Every value fits in a signed 32-bit integer.

## Example
values = [5,1,8,4], goal = 12 → [2,3]

## Approach
Walk the list once while remembering the position of every value you have already passed. At position j, look up `goal - values[j]`; if that partner value was seen earlier, you have found the pair. Otherwise record the current value and move on. Time O(n), space O(n).

## Hints
- For each entry, ask which partner value would complete the goal, and whether you have already passed it.
- Look up the partner before recording the current entry, so an entry is never paired with itself.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def two_sum(values, goal):
    seen = {}
    for j, v in enumerate(values):
        i = seen.get(goal - v)
        if i is not None:
            return [i, j]
        seen[v] = j
    return []
```

### JavaScript
```javascript
function twoSum(values, goal) {
  const seen = new Map();
  for (let j = 0; j < values.length; j++) {
    const i = seen.get(goal - values[j]);
    if (i !== undefined) return [i, j];
    seen.set(values[j], j);
  }
  return [];
}
```

### TypeScript
```typescript
function twoSum(values: number[], goal: number): number[] {
  const seen = new Map<number, number>();
  for (let j = 0; j < values.length; j++) {
    const i = seen.get(goal - values[j]);
    if (i !== undefined) return [i, j];
    seen.set(values[j], j);
  }
  return [];
}
```

### Java
```java
public int[] twoSum(int[] values, int goal) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int j = 0; j < values.length; j++) {
        Integer i = seen.get(goal - values[j]);
        if (i != null) return new int[]{i, j};
        seen.put(values[j], j);
    }
    return new int[0];
}
```

### C++
```cpp
#include <unordered_map>
#include <vector>
std::vector<int> two_sum(std::vector<int>& values, int goal) {
    std::unordered_map<int, int> seen;
    for (int j = 0; j < (int)values.size(); j++) {
        auto it = seen.find(goal - values[j]);
        if (it != seen.end()) return {it->second, j};
        seen[values[j]] = j;
    }
    return {};
}
```

### C
```c
/* Open-addressing hash table keyed by value, storing positions. */
int* two_sum(int* values, int valuesSize, int goal, int* returnSize) {
    int cap = valuesSize * 2 + 1;
    int* keys = malloc(cap * sizeof(int));
    int* where = malloc(cap * sizeof(int));
    char* used = calloc(cap, 1);
    int* res = malloc(2 * sizeof(int));
    *returnSize = 0;
    for (int j = 0; j < valuesSize; j++) {
        long want = (long)goal - values[j];
        unsigned h = (unsigned)(want % cap + cap) % cap;
        while (used[h]) {
            if (keys[h] == want) {
                res[0] = where[h]; res[1] = j; *returnSize = 2;
                free(keys); free(where); free(used);
                return res;
            }
            h = (h + 1) % cap;
        }
        unsigned h2 = (unsigned)((long)values[j] % cap + cap) % cap;
        while (used[h2]) h2 = (h2 + 1) % cap;
        used[h2] = 1; keys[h2] = values[j]; where[h2] = j;
    }
    free(keys); free(where); free(used);
    return res;
}
```

### Rust
```rust
use std::collections::HashMap;
pub fn two_sum(values: Vec<i32>, goal: i32) -> Vec<i32> {
    let mut seen: HashMap<i32, i32> = HashMap::new();
    for (j, &v) in values.iter().enumerate() {
        if let Some(&i) = seen.get(&(goal - v)) {
            return vec![i, j as i32];
        }
        seen.insert(v, j as i32);
    }
    vec![]
}
```

### Go
```go
func twoSum(values []int, goal int) []int {
	seen := make(map[int]int)
	for j, v := range values {
		if i, ok := seen[goal-v]; ok {
			return []int{i, j}
		}
		seen[v] = j
	}
	return []int{}
}
```

### C#
```csharp
public static int[] TwoSum(int[] values, int goal)
{
    var seen = new System.Collections.Generic.Dictionary<int, int>();
    for (int j = 0; j < values.Length; j++)
    {
        if (seen.TryGetValue(goal - values[j], out int i)) return new int[] { i, j };
        seen[values[j]] = j;
    }
    return new int[0];
}
```

### Ruby
```ruby
def two_sum(values, goal)
  seen = {}
  values.each_with_index do |v, j|
    return [seen[goal - v], j] if seen.key?(goal - v)
    seen[v] = j
  end
  []
end
```
