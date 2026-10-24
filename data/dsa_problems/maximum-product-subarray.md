---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays, dynamic-programming
fn_python: max_product
fn_javascript: maxProduct
fn_typescript: maxProduct
fn_java: maxProduct
fn_cpp: maxProduct
fn_c: maxProduct
fn_rust: max_product
fn_go: maxProduct
fn_csharp: MaxProduct
fn_ruby: max_product
test_cases: [{"args": [[7]], "expected": 7}, {"args": [[-6]], "expected": -6}, {"args": [[0, -4, 0]], "expected": 0}, {"args": [[1, -1, 1, -1]], "expected": 1}, {"args": [[2, -5, -3, 0, 4]], "expected": 30}, {"args": [[-1, -1, -1]], "expected": 1}, {"args": [[3, 0, -2, -2, 6]], "expected": 24}, {"args": [[-2, 3, -4, 5, -1]], "expected": 120}]
---
# Largest Product Run — Medium — Array, DP

## Problem
Given a non-empty list `values` of integers, choose one run of consecutive entries (a start index and an end index with start <= end, keeping every entry between them). The run must contain at least one entry. Return the largest product of the entries in any such run as an integer.

## Example
values = [-3,5,-2,-4] → 40 (the run 5, -2, -4 has product 40)

## Approach
Track two values while walking the list: the largest product of a run ending at the current position and the smallest such product. A negative entry turns the largest into the smallest and the reverse, so swap the two before applying the current entry. Take the larger of the new maximum and the current entry, and the smaller of the new minimum and the current entry. Record the best maximum seen. Time O(n), space O(1).

## Hints
- Why does a plain running maximum fail? A negative entry can turn the smallest product into the largest.
- When the current entry is negative, swap the running maximum and running minimum before you update them.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions.*

### Python
```python
def max_product(values):
    best = hi = lo = values[0]
    for x in values[1:]:
        if x < 0:
            hi, lo = lo, hi
        hi = max(x, hi * x)
        lo = min(x, lo * x)
        best = max(best, hi)
    return best
```

### JavaScript
```javascript
function maxProduct(values) {
  let best = values[0], hi = values[0], lo = values[0];
  for (let i = 1; i < values.length; i++) {
    const x = values[i];
    if (x < 0) [hi, lo] = [lo, hi];
    hi = Math.max(x, hi * x);
    lo = Math.min(x, lo * x);
    best = Math.max(best, hi);
  }
  return best;
}
```

### TypeScript
```typescript
function maxProduct(values: number[]): number {
  let best = values[0], hi = values[0], lo = values[0];
  for (let i = 1; i < values.length; i++) {
    const x = values[i];
    if (x < 0) [hi, lo] = [lo, hi];
    hi = Math.max(x, hi * x);
    lo = Math.min(x, lo * x);
    best = Math.max(best, hi);
  }
  return best;
}
```

### Java
```java
public int maxProduct(int[] values) {
    int best = values[0], hi = values[0], lo = values[0];
    for (int i = 1; i < values.length; i++) {
        int x = values[i];
        if (x < 0) { int t = hi; hi = lo; lo = t; }
        hi = Math.max(x, hi * x);
        lo = Math.min(x, lo * x);
        best = Math.max(best, hi);
    }
    return best;
}
```

### C++
```cpp
int maxProduct(std::vector<int>& values) {
    int best = values[0], hi = values[0], lo = values[0];
    for (size_t i = 1; i < values.size(); i++) {
        int x = values[i];
        if (x < 0) std::swap(hi, lo);
        hi = std::max(x, hi * x);
        lo = std::min(x, lo * x);
        best = std::max(best, hi);
    }
    return best;
}
```

### C
```c
long long maxProduct(long long* values, int valuesSize) {
    long long best = values[0], hi = values[0], lo = values[0];
    for (int i = 1; i < valuesSize; i++) {
        long long x = values[i];
        if (x < 0) { long long t = hi; hi = lo; lo = t; }
        long long cand = hi * x;
        hi = x > cand ? x : cand;
        cand = lo * x;
        lo = x < cand ? x : cand;
        if (hi > best) best = hi;
    }
    return best;
}
```

### Rust
```rust
pub fn max_product(values: Vec<i32>) -> i32 {
    let mut best = values[0];
    let mut hi = values[0];
    let mut lo = values[0];
    for &x in &values[1..] {
        if x < 0 {
            std::mem::swap(&mut hi, &mut lo);
        }
        hi = x.max(hi * x);
        lo = x.min(lo * x);
        best = best.max(hi);
    }
    best
}
```

### Go
```go
func maxProduct(values []int) int {
	best, hi, lo := values[0], values[0], values[0]
	for _, x := range values[1:] {
		if x < 0 {
			hi, lo = lo, hi
		}
		cand := hi * x
		if x > cand {
			hi = x
		} else {
			hi = cand
		}
		cand = lo * x
		if x < cand {
			lo = x
		} else {
			lo = cand
		}
		if hi > best {
			best = hi
		}
	}
	return best
}
```

### C#
```csharp
public static int MaxProduct(int[] values)
{
    int best = values[0], hi = values[0], lo = values[0];
    for (int i = 1; i < values.Length; i++)
    {
        int x = values[i];
        if (x < 0) { int t = hi; hi = lo; lo = t; }
        int up = hi * x;
        hi = x > up ? x : up;
        int down = lo * x;
        lo = x < down ? x : down;
        if (hi > best) best = hi;
    }
    return best;
}
```

### Ruby
```ruby
def max_product(values)
  best = hi = lo = values[0]
  values.drop(1).each do |x|
    hi, lo = lo, hi if x < 0
    hi = [x, hi * x].max
    lo = [x, lo * x].min
    best = [best, hi].max
  end
  best
end
```
