---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: product_except_index
fn_javascript: productExceptIndex
fn_typescript: productExceptIndex
fn_java: productExceptIndex
fn_cpp: product_except_index
fn_c: product_except_index
fn_rust: product_except_index
fn_go: productExceptIndex
fn_csharp: ProductExceptIndex
fn_ruby: product_except_index
test_cases: [{"args": [[]], "expected": []}, {"args": [[7]], "expected": [1]}, {"args": [[2, -3, 4]], "expected": [-12, 8, -6]}, {"args": [[1, 1, 1, 1]], "expected": [1, 1, 1, 1]}, {"args": [[-1, -1]], "expected": [-1, -1]}, {"args": [[5, 6]], "expected": [6, 5]}, {"args": [[3, -2, 1, -1, 2]], "expected": [4, -6, 12, -12, 6]}, {"args": [[9, 10, -11, 12, -13]], "expected": [17160, 15444, -14040, 12870, -11880]}]
---

# All But One Product — Medium — Arrays and Hashing

## Problem
Given a list `values` of nonzero integers, return a list `out` of the same length where `out[i]` is the product of every element of `values` except `values[i]`. Division is not allowed in the solution. Every product in the answer has an absolute value of at most 9007199254740991 (2^53 - 1), so each one is exact in JavaScript's floating-point numbers as well as in the other languages. For an empty list return an empty list. For a single-element list the product of no other values is 1, so return `[1]`.

## Example
values = [2,-3,4] → [-12,8,-6] (for index 0 the others multiply to -3 * 4 = -12; for index 1 they give 2 * 4 = 8; for index 2 they give 2 * -3 = -6)

## Approach
Make one left-to-right pass that writes into the output the product of everything strictly left of each index (a running prefix product). Then make one right-to-left pass that multiplies each stored entry by a running suffix product, the product of everything strictly right of the index. Each output entry is its prefix times its suffix, with no division. Time O(n), with only the output as extra storage.

## Hints
- The prefix before index i is the product of values[0] through values[i-1]; an empty prefix is 1.
- Write the prefixes into the output in the first pass, then multiply by the suffixes in the second.
- Keep the two running products in separate variables so the passes do not interfere.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def product_except_index(values):
    n = len(values)
    out = [1] * n
    prefix = 1
    for i in range(n):
        out[i] = prefix
        prefix *= values[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= values[i]
    return out
```

### JavaScript
```javascript
function productExceptIndex(values) {
  const n = values.length;
  const out = new Array(n).fill(1);
  let prefix = 1;
  for (let i = 0; i < n; i++) {
    out[i] = prefix;
    prefix *= values[i];
  }
  let suffix = 1;
  for (let i = n - 1; i >= 0; i--) {
    out[i] *= suffix;
    suffix *= values[i];
  }
  return out;
}
```

### TypeScript
```typescript
function productExceptIndex(values: number[]): number[] {
  const n = values.length;
  const out: number[] = new Array(n).fill(1);
  let prefix = 1;
  for (let i = 0; i < n; i++) {
    out[i] = prefix;
    prefix *= values[i];
  }
  let suffix = 1;
  for (let i = n - 1; i >= 0; i--) {
    out[i] *= suffix;
    suffix *= values[i];
  }
  return out;
}
```

### Java
```java
public long[] productExceptIndex(long[] values) {
    int n = values.length;
    long[] out = new long[n];
    long prefix = 1;
    for (int i = 0; i < n; i++) {
        out[i] = prefix;
        prefix *= values[i];
    }
    long suffix = 1;
    for (int i = n - 1; i >= 0; i--) {
        out[i] *= suffix;
        suffix *= values[i];
    }
    return out;
}
```

### C++
```cpp
#include <vector>
std::vector<long long> product_except_index(std::vector<long long>& values) {
    size_t n = values.size();
    std::vector<long long> out(n, 1);
    long long prefix = 1;
    for (size_t i = 0; i < n; i++) {
        out[i] = prefix;
        prefix *= values[i];
    }
    long long suffix = 1;
    for (size_t i = n; i-- > 0;) {
        out[i] *= suffix;
        suffix *= values[i];
    }
    return out;
}
```

### C
```c
long long* product_except_index(long long* values, int valuesSize, int* returnSize) {
    long long* out = malloc((valuesSize + 1) * sizeof(long long));
    *returnSize = valuesSize;
    long long prefix = 1;
    for (int i = 0; i < valuesSize; i++) {
        out[i] = prefix;
        prefix *= values[i];
    }
    long long suffix = 1;
    for (int i = valuesSize - 1; i >= 0; i--) {
        out[i] *= suffix;
        suffix *= values[i];
    }
    return out;
}
```

### Rust
```rust
pub fn product_except_index(values: Vec<i64>) -> Vec<i64> {
    let n = values.len();
    let mut out = vec![1i64; n];
    let mut prefix = 1i64;
    for i in 0..n {
        out[i] = prefix;
        prefix *= values[i];
    }
    let mut suffix = 1i64;
    for i in (0..n).rev() {
        out[i] *= suffix;
        suffix *= values[i];
    }
    out
}
```

### Go
```go
func productExceptIndex(values []int) []int {
	n := len(values)
	out := make([]int, n)
	prefix := 1
	for i := 0; i < n; i++ {
		out[i] = prefix
		prefix *= values[i]
	}
	suffix := 1
	for i := n - 1; i >= 0; i-- {
		out[i] *= suffix
		suffix *= values[i]
	}
	return out
}
```

### C#
```csharp
public static long[] ProductExceptIndex(long[] values)
{
    int n = values.Length;
    long[] output = new long[n];
    long prefix = 1;
    for (int i = 0; i < n; i++)
    {
        output[i] = prefix;
        prefix *= values[i];
    }
    long suffix = 1;
    for (int i = n - 1; i >= 0; i--)
    {
        output[i] *= suffix;
        suffix *= values[i];
    }
    return output;
}
```

### Ruby
```ruby
def product_except_index(values)
  n = values.length
  out = Array.new(n, 1)
  prefix = 1
  n.times do |i|
    out[i] = prefix
    prefix *= values[i]
  end
  suffix = 1
  (n - 1).downto(0) do |i|
    out[i] *= suffix
    suffix *= values[i]
  end
  out
end
```
