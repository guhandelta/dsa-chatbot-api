---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: bit-manipulation, math
fn_python: missing_number
fn_javascript: missingNumber
fn_typescript: missingNumber
fn_java: missingNumber
fn_cpp: missingNumber
fn_c: missingNumber
fn_rust: missing_number
fn_go: missingNumber
fn_csharp: MissingNumber
fn_ruby: missing_number
test_cases: [{"args": [[]], "expected": 0}, {"args": [[0]], "expected": 1}, {"args": [[1]], "expected": 0}, {"args": [[5, 2, 0, 3, 1]], "expected": 4}, {"args": [[6, 0, 1, 2, 4, 5]], "expected": 3}, {"args": [[0, 1, 2, 3, 4, 5, 6, 7, 9]], "expected": 8}, {"args": [[2, 0]], "expected": 1}, {"args": [[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]], "expected": 0}]
---
# Find the Hole in a Range — Easy — Bit Manipulation / Math

## Problem
Given a list `values` of n distinct integers, where every integer lies in the range 0 through n inclusive, exactly one integer of that range is absent from the list. Return the absent integer. The list may be empty, in which case the range is just 0 and the answer is 0.

## Example
values = [1,4,0,3] → 2 (the range is 0 through 4, and 2 is the only value not present)

## Approach
Combine the index of every position with the value stored there, using XOR, together with n itself. Every value that is present cancels against its matching index, so only the absent value survives. Time O(n), space O(1). A sum-based formula also works, but XOR avoids overflow in fixed-width languages.

## Hints
- XOR-ing a value with itself gives 0, and the order of XOR does not matter.
- Pair each index 0..n-1 with the entry at that index, then add n to the mix.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions.*

### Python
```python
def missing_number(values):
    total = len(values)
    for i, v in enumerate(values):
        total ^= i ^ v
    return total
```

### JavaScript
```javascript
function missingNumber(values) {
  let total = values.length;
  for (let i = 0; i < values.length; i++) total ^= i ^ values[i];
  return total;
}
```

### TypeScript
```typescript
function missingNumber(values: number[]): number {
  let total = values.length;
  for (let i = 0; i < values.length; i++) total ^= i ^ values[i];
  return total;
}
```

### Java
```java
public int missingNumber(int[] values) {
    int total = values.length;
    for (int i = 0; i < values.length; i++) total ^= i ^ values[i];
    return total;
}
```

### C++
```cpp
int missingNumber(std::vector<int>& values) {
    int total = values.size();
    for (int i = 0; i < (int)values.size(); i++) total ^= i ^ values[i];
    return total;
}
```

### C
```c
int missingNumber(int* values, int valuesSize) {
    int total = valuesSize;
    for (int i = 0; i < valuesSize; i++) total ^= i ^ values[i];
    return total;
}
```

### Rust
```rust
pub fn missing_number(values: Vec<i32>) -> i32 {
    let mut total = values.len() as i32;
    for (i, &v) in values.iter().enumerate() {
        total ^= i as i32 ^ v;
    }
    total
}
```

### Go
```go
func missingNumber(values []int) int {
	total := len(values)
	for i, v := range values {
		total ^= i ^ v
	}
	return total
}
```

### C#
```csharp
public static int MissingNumber(int[] values)
{
    int total = values.Length;
    for (int i = 0; i < values.Length; i++) total ^= i ^ values[i];
    return total;
}
```

### Ruby
```ruby
def missing_number(values)
  total = values.length
  values.each_with_index { |v, i| total ^= i ^ v }
  total
end
```
