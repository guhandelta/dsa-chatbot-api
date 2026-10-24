---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays, dynamic-programming, kadane
fn_python: max_sub_array
fn_javascript: maxSubArray
fn_typescript: maxSubArray
fn_java: maxSubArray
fn_cpp: maxSubArray
fn_c: maxSubArray
fn_rust: max_sub_array
fn_go: maxSubArray
fn_csharp: MaxSubArray
fn_ruby: max_sub_array
test_cases: [{"args": [[7]], "expected": 7}, {"args": [[-5]], "expected": -5}, {"args": [[6, -1, -1, 6]], "expected": 10}, {"args": [[-3, -8, -1, -6]], "expected": -1}, {"args": [[2, -3, 5, -1, -2, 4, -4, 3]], "expected": 6}, {"args": [[0, 0, 0, 0]], "expected": 0}, {"args": [[1000000, -1, 1000000]], "expected": 1999999}, {"args": [[-4, 2, 2, -9, 1, 1, 1]], "expected": 4}, {"args": [[5, -5, 5, -5, 5]], "expected": 5}]
---
# Best Consecutive Run Sum — Medium — Array, Kadane's Algorithm / DP

## Problem
Given a non-empty list `values` of integers, pick one run of consecutive entries (a start index and an end index with start <= end, keeping every entry between them) so that the sum of the run is as large as possible. The run must contain at least one entry, and it may contain negative numbers. Return that largest sum as an integer.

## Example
values = [4,-7,3,3,-2,5] → 9 (the run 3, 3, -2, 5 sums to 9)

## Approach
Walk the list once while tracking the best run that ends at the current position. Extending the previous best run by the current value is only worth it when that run is not already negative; otherwise start a fresh run at the current value. Keep the largest run total seen at any position. Time O(n), space O(1).

## Hints
- If the best run ending just before position i has a negative total, dropping it can only help.
- For each position, the best run ending there is either that value alone or that value added to the best run ending at the previous position.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions.*

### Python
```python
def max_sub_array(values):
    run_best = run_end = values[0]
    for v in values[1:]:
        run_end = max(v, run_end + v)
        run_best = max(run_best, run_end)
    return run_best
```

### JavaScript
```javascript
function maxSubArray(values) {
  let runBest = values[0], runEnd = values[0];
  for (let i = 1; i < values.length; i++) {
    runEnd = Math.max(values[i], runEnd + values[i]);
    runBest = Math.max(runBest, runEnd);
  }
  return runBest;
}
```

### TypeScript
```typescript
function maxSubArray(values: number[]): number {
  let runBest = values[0], runEnd = values[0];
  for (let i = 1; i < values.length; i++) {
    runEnd = Math.max(values[i], runEnd + values[i]);
    runBest = Math.max(runBest, runEnd);
  }
  return runBest;
}
```

### Java
```java
public int maxSubArray(int[] values) {
    int runBest = values[0], runEnd = values[0];
    for (int i = 1; i < values.length; i++) {
        runEnd = Math.max(values[i], runEnd + values[i]);
        runBest = Math.max(runBest, runEnd);
    }
    return runBest;
}
```

### C++
```cpp
int maxSubArray(std::vector<int>& values) {
    int runBest = values[0], runEnd = values[0];
    for (size_t i = 1; i < values.size(); i++) {
        runEnd = std::max(values[i], runEnd + values[i]);
        runBest = std::max(runBest, runEnd);
    }
    return runBest;
}
```

### C
```c
long long maxSubArray(long long* values, int valuesSize) {
    long long runBest = values[0], runEnd = values[0];
    for (int i = 1; i < valuesSize; i++) {
        long long extend = runEnd + values[i];
        runEnd = values[i] > extend ? values[i] : extend;
        if (runEnd > runBest) runBest = runEnd;
    }
    return runBest;
}
```

### Rust
```rust
pub fn max_sub_array(values: Vec<i32>) -> i32 {
    let mut run_best = values[0];
    let mut run_end = values[0];
    for &v in &values[1..] {
        run_end = v.max(run_end + v);
        run_best = run_best.max(run_end);
    }
    run_best
}
```

### Go
```go
func maxSubArray(values []int) int {
	runBest, runEnd := values[0], values[0]
	for _, v := range values[1:] {
		extend := runEnd + v
		if v > extend {
			runEnd = v
		} else {
			runEnd = extend
		}
		if runEnd > runBest {
			runBest = runEnd
		}
	}
	return runBest
}
```

### C#
```csharp
public static int MaxSubArray(int[] values)
{
    int runBest = values[0], runEnd = values[0];
    for (int i = 1; i < values.Length; i++)
    {
        int extend = runEnd + values[i];
        runEnd = values[i] > extend ? values[i] : extend;
        if (runEnd > runBest) runBest = runEnd;
    }
    return runBest;
}
```

### Ruby
```ruby
def max_sub_array(values)
  run_best = run_end = values[0]
  values.drop(1).each do |v|
    run_end = [v, run_end + v].max
    run_best = [run_best, run_end].max
  end
  run_best
end
```
