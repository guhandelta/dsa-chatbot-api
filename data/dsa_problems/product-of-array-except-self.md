---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays, prefix-sum
fn_python: product_except_self
fn_javascript: productExceptSelf
fn_typescript: productExceptSelf
fn_java: productExceptSelf
fn_cpp: productExceptSelf
fn_c: productExceptSelf
fn_rust: product_except_self
fn_go: productExceptSelf
fn_csharp: ProductExceptSelf
fn_ruby: product_except_self
test_cases: [{"args": [[4]], "expected": [1]}, {"args": [[0, 3, 5]], "expected": [15, 0, 0]}, {"args": [[3, 6, 2]], "expected": [12, 6, 18]}, {"args": [[-2, -3]], "expected": [-3, -2]}, {"args": [[1, 0, 0]], "expected": [0, 0, 0]}, {"args": [[-1, 0, 4, -2]], "expected": [0, 8, 0, 0]}, {"args": [[7, 7, 7, 7, 7]], "expected": [2401, 2401, 2401, 2401, 2401]}, {"args": [[10, -10, 10]], "expected": [-100, 100, -100]}, {"args": [[2, -1, 0, -3]], "expected": [0, 0, 6, 0]}]
---
# Product Excluding Each Position — Medium — Array, Prefix Product

## Problem
Given a non-empty list `values` of integers, return a new list `res` of the same length where `res[i]` is the product of all entries of `values` except the entry at index i. An empty product is 1, so a one-element list gives `[1]`. Division is not allowed, and the solution must run in O(n) time. Every product in the answer fits in a 32-bit signed integer.

## Example
values = [2,5,-1,3] → [-15,-6,30,-10]

## Approach
Use two sweeps. The first sweep writes into the result the product of everything to the left of each position, carrying a running prefix product. The second sweep walks from the right, multiplying each stored entry by a running suffix product of everything to its right. Each result entry is then its prefix times its suffix. Time O(n), with only the result as extra storage.

## Hints
- res[i] is (product of the entries before i) times (product of the entries after i).
- Store the prefix products in the result array first, then fold in the suffix products in a second pass.
- Keep the prefix and the suffix in separate variables so the two passes do not interfere.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def product_except_self(values):
    size = len(values)
    res = [1] * size
    pre = 1
    for i in range(size):
        res[i] = pre
        pre *= values[i]
    post = 1
    for i in range(size - 1, -1, -1):
        res[i] *= post
        post *= values[i]
    return res
```

### JavaScript
```javascript
function productExceptSelf(values) {
  const size = values.length, res = new Array(size).fill(1);
  let pre = 1;
  for (let i = 0; i < size; i++) {
    res[i] = pre;
    pre *= values[i];
  }
  let post = 1;
  for (let i = size - 1; i >= 0; i--) {
    res[i] *= post;
    post *= values[i];
  }
  return res;
}
```

### TypeScript
```typescript
function productExceptSelf(values: number[]): number[] {
  const size = values.length, res: number[] = new Array(size).fill(1);
  let pre = 1;
  for (let i = 0; i < size; i++) {
    res[i] = pre;
    pre *= values[i];
  }
  let post = 1;
  for (let i = size - 1; i >= 0; i--) {
    res[i] *= post;
    post *= values[i];
  }
  return res;
}
```

### Java
```java
public int[] productExceptSelf(int[] values) {
    int size = values.length;
    int[] res = new int[size];
    int pre = 1;
    for (int i = 0; i < size; i++) {
        res[i] = pre;
        pre *= values[i];
    }
    int post = 1;
    for (int i = size - 1; i >= 0; i--) {
        res[i] *= post;
        post *= values[i];
    }
    return res;
}
```

### C++
```cpp
std::vector<int> productExceptSelf(std::vector<int>& values) {
    size_t size = values.size();
    std::vector<int> res(size, 1);
    int pre = 1;
    for (size_t i = 0; i < size; i++) {
        res[i] = pre;
        pre *= values[i];
    }
    int post = 1;
    for (size_t i = size; i-- > 0;) {
        res[i] *= post;
        post *= values[i];
    }
    return res;
}
```

### C
```c
long long* productExceptSelf(long long* values, int valuesSize, int* returnSize) {
    long long* res = malloc(valuesSize * sizeof(long long));
    *returnSize = valuesSize;
    long long pre = 1;
    for (int i = 0; i < valuesSize; i++) {
        res[i] = pre;
        pre *= values[i];
    }
    long long post = 1;
    for (int i = valuesSize - 1; i >= 0; i--) {
        res[i] *= post;
        post *= values[i];
    }
    return res;
}
```

### Rust
```rust
pub fn product_except_self(values: Vec<i32>) -> Vec<i32> {
    let size = values.len();
    let mut res = vec![1; size];
    let mut pre = 1;
    for i in 0..size {
        res[i] = pre;
        pre *= values[i];
    }
    let mut post = 1;
    for i in (0..size).rev() {
        res[i] *= post;
        post *= values[i];
    }
    res
}
```

### Go
```go
func productExceptSelf(values []int) []int {
	size := len(values)
	res := make([]int, size)
	pre := 1
	for i := 0; i < size; i++ {
		res[i] = pre
		pre *= values[i]
	}
	post := 1
	for i := size - 1; i >= 0; i-- {
		res[i] *= post
		post *= values[i]
	}
	return res
}
```

### C#
```csharp
public static int[] ProductExceptSelf(int[] values)
{
    int size = values.Length;
    int[] res = new int[size];
    int pre = 1;
    for (int i = 0; i < size; i++)
    {
        res[i] = pre;
        pre *= values[i];
    }
    int post = 1;
    for (int i = size - 1; i >= 0; i--)
    {
        res[i] *= post;
        post *= values[i];
    }
    return res;
}
```

### Ruby
```ruby
def product_except_self(values)
  size = values.length
  res = Array.new(size, 1)
  pre = 1
  size.times { |i| res[i] = pre; pre *= values[i] }
  post = 1
  (size - 1).downto(0) { |i| res[i] *= post; post *= values[i] }
  res
end
```
