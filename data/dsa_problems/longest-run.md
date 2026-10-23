---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: longest_run
fn_javascript: longestRun
fn_typescript: longestRun
fn_java: longestRun
fn_cpp: longest_run
fn_c: longest_run
fn_rust: longest_run
fn_go: longestRun
fn_csharp: LongestRun
fn_ruby: longest_run
test_cases: [{"args": [[]], "expected": 0}, {"args": [[42]], "expected": 1}, {"args": [[5, 5, 5]], "expected": 1}, {"args": [[1, 2, 3, 4, 5]], "expected": 5}, {"args": [[3, 1, 2, 100, 101]], "expected": 3}, {"args": [[-4, -3, -1, 0, 1, 2, 8]], "expected": 4}, {"args": [[9, 1, 4, 7, 3, 2]], "expected": 4}, {"args": [[1000000000001, 1000000000000, 999999999999, 5]], "expected": 3}, {"args": [[10, -2, 7, 8, -1, 9, 0, 11, 8, -2]], "expected": 5}]
---

# Longest Run — Medium — Arrays and Hashing

## Problem
Given a list of integers `values`, which may contain repeated and negative numbers, find the longest run of consecutive integers that can be formed from its distinct values. A run is a set of integers that form an unbroken range such as 4, 5, 6, 7; the order in which the values appear in `values` does not matter. Repeated values are ignored. Return the number of integers in the longest run. If `values` is empty, return 0.

## Example
values = [10,-2,7,8,-1,9,0,11,8,-2] → 5 (the run 7, 8, 9, 10, 11 has five integers; the run -2, -1, 0 has three)

## Approach
Put the values into a hash set. A run can only begin at a value `x` whose predecessor `x - 1` is absent from the set, so only those values are used as starts. From each start, count upward while `x + 1`, `x + 2`, and so on are present. Every value is walked by at most one run, the one that starts below it, so the total work is linear. Time O(n), space O(n).

## Hints
- Skip any x whose predecessor x - 1 is in the set; it is not the start of a run.
- A set discards duplicates automatically.
- Counting upward only from run starts touches each value once overall.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def longest_run(values):
    present = set(values)
    best = 0
    for x in present:
        if x - 1 in present:
            continue
        length = 1
        while x + length in present:
            length += 1
        best = max(best, length)
    return best
```

### JavaScript
```javascript
function longestRun(values) {
  const present = new Set(values);
  let best = 0;
  for (const x of present) {
    if (present.has(x - 1)) continue;
    let length = 1;
    while (present.has(x + length)) length++;
    best = Math.max(best, length);
  }
  return best;
}
```

### TypeScript
```typescript
function longestRun(values: number[]): number {
  const present = new Set<number>(values);
  let best = 0;
  for (const x of present) {
    if (present.has(x - 1)) continue;
    let length = 1;
    while (present.has(x + length)) length++;
    best = Math.max(best, length);
  }
  return best;
}
```

### Java
```java
public long longestRun(long[] values) {
    Set<Long> present = new HashSet<>();
    for (long v : values) present.add(v);
    long best = 0;
    for (long x : present) {
        if (present.contains(x - 1)) continue;
        long length = 1;
        while (present.contains(x + length)) length++;
        best = Math.max(best, length);
    }
    return best;
}
```

### C++
```cpp
#include <algorithm>
#include <unordered_set>
#include <vector>
long long longest_run(std::vector<long long>& values) {
    std::unordered_set<long long> present(values.begin(), values.end());
    long long best = 0;
    for (long long x : present) {
        if (present.count(x - 1)) continue;
        long long length = 1;
        while (present.count(x + length)) length++;
        best = std::max(best, length);
    }
    return best;
}
```

### C
```c
static int cmp_ll(const void* a, const void* b) {
    long long x = *(const long long*)a, y = *(const long long*)b;
    return (x > y) - (x < y);
}
long long longest_run(long long* values, int valuesSize) {
    if (valuesSize == 0) return 0;
    long long* sorted = malloc(valuesSize * sizeof(long long));
    memcpy(sorted, values, valuesSize * sizeof(long long));
    qsort(sorted, valuesSize, sizeof(long long), cmp_ll);
    long long best = 1, length = 1;
    for (int i = 1; i < valuesSize; i++) {
        if (sorted[i] == sorted[i - 1]) continue;
        length = (sorted[i] == sorted[i - 1] + 1) ? length + 1 : 1;
        if (length > best) best = length;
    }
    free(sorted);
    return best;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn longest_run(values: Vec<i64>) -> i64 {
    let present: HashSet<i64> = values.into_iter().collect();
    let mut best = 0i64;
    for &x in &present {
        if present.contains(&(x - 1)) {
            continue;
        }
        let mut length = 1i64;
        while present.contains(&(x + length)) {
            length += 1;
        }
        if length > best {
            best = length;
        }
    }
    best
}
```

### Go
```go
func longestRun(values []int) int {
	present := make(map[int]bool)
	for _, v := range values {
		present[v] = true
	}
	best := 0
	for x := range present {
		if present[x-1] {
			continue
		}
		length := 1
		for present[x+length] {
			length++
		}
		if length > best {
			best = length
		}
	}
	return best
}
```

### C#
```csharp
public static long LongestRun(long[] values)
{
    var present = new System.Collections.Generic.HashSet<long>(values);
    long best = 0;
    foreach (long x in present)
    {
        if (present.Contains(x - 1)) continue;
        long length = 1;
        while (present.Contains(x + length)) length++;
        best = System.Math.Max(best, length);
    }
    return best;
}
```

### Ruby
```ruby
def longest_run(values)
  present = {}
  values.each { |v| present[v] = true }
  best = 0
  present.each_key do |x|
    next if present.key?(x - 1)
    length = 1
    length += 1 while present.key?(x + length)
    best = length if length > best
  end
  best
end
```
