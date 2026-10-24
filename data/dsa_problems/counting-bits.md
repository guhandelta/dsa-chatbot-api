---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: bit-manipulation, dynamic-programming
fn_python: count_bits
fn_javascript: countBits
fn_typescript: countBits
fn_java: countBits
fn_cpp: countBits
fn_c: countBits
fn_rust: count_bits
fn_go: countBits
fn_csharp: CountBits
fn_ruby: count_bits
test_cases: [{"args": [0], "expected": [0]}, {"args": [1], "expected": [0, 1]}, {"args": [4], "expected": [0, 1, 1, 2, 1]}, {"args": [7], "expected": [0, 1, 1, 2, 1, 2, 2, 3]}, {"args": [9], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1, 2]}, {"args": [10], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2]}, {"args": [12], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2]}, {"args": [15], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4]}]
---
# Set-Bit Counts Up to a Limit — Easy — DP, Bit Manipulation

## Problem
Given a non-negative integer `limit`, return a list whose entry at index i, for every i from 0 through `limit` inclusive, is the number of 1 bits in the binary form of i. The list therefore has `limit + 1` entries. Aim for O(limit) time.

## Example
limit = 6 → [0,1,1,2,1,2,2]

## Approach
Build the answer from left to right. The count for i equals the count for i shifted right by one (that is, i with its lowest bit removed) plus the lowest bit of i itself. Each value is looked up from an earlier entry, so the whole table takes O(limit) time and O(limit) space for the output.

## Hints
- Shifting i right by one drops its lowest bit, and the lowest bit contributes 0 or 1 to the count.
- An alternative: the count for i equals the count for (i AND (i - 1)) plus 1.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def count_bits(limit):
    ones = [0] * (limit + 1)
    for i in range(1, limit + 1):
        ones[i] = ones[i >> 1] + (i & 1)
    return ones
```

### JavaScript
```javascript
function countBits(limit) {
  const ones = new Array(limit + 1).fill(0);
  for (let i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
  return ones;
}
```

### TypeScript
```typescript
function countBits(limit: number): number[] {
  const ones: number[] = new Array(limit + 1).fill(0);
  for (let i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
  return ones;
}
```

### Java
```java
public int[] countBits(int limit) {
    int[] ones = new int[limit + 1];
    for (int i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
    return ones;
}
```

### C++
```cpp
std::vector<int> countBits(int limit) {
    std::vector<int> ones(limit + 1, 0);
    for (int i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
    return ones;
}
```

### C
```c
int* countBits(int limit, int* returnSize) {
    int* ones = calloc(limit + 1, sizeof(int));
    *returnSize = limit + 1;
    for (int i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
    return ones;
}
```

### Rust
```rust
pub fn count_bits(limit: i32) -> Vec<i32> {
    let top = limit as usize;
    let mut ones = vec![0; top + 1];
    for i in 1..=top {
        ones[i] = ones[i >> 1] + ((i & 1) as i32);
    }
    ones
}
```

### Go
```go
func countBits(limit int) []int {
	ones := make([]int, limit+1)
	for i := 1; i <= limit; i++ {
		ones[i] = ones[i>>1] + (i & 1)
	}
	return ones
}
```

### C#
```csharp
public static int[] CountBits(int limit)
{
    int[] ones = new int[limit + 1];
    for (int i = 1; i <= limit; i++) ones[i] = ones[i >> 1] + (i & 1);
    return ones;
}
```

### Ruby
```ruby
def count_bits(limit)
  ones = Array.new(limit + 1, 0)
  (1..limit).each { |i| ones[i] = ones[i >> 1] + (i & 1) }
  ones
end
```
