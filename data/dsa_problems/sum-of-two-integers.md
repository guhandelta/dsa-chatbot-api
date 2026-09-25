---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: bit-manipulation
fn_python: get_sum
fn_javascript: getSum
test_cases: [{"args": [1, 2], "expected": 3}, {"args": [-2, 3], "expected": 1}, {"args": [0, 0], "expected": 0}, {"args": [-1, -1], "expected": -2}, {"args": [5, -5], "expected": 0}, {"args": [1000, 2000], "expected": 3000}]
---
# Sum of Two Integers (LC 371) — Medium — Bit Manipulation

## Problem
Compute a + b without using the + or - operators.

## Example
a = 1, b = 2 → 3

## Approach
XOR adds without carries; AND shifted left by one produces the carries. Repeat until the carry is zero. Languages with unbounded ints (Python) need a 32-bit mask. Time O(1) (≤32 iterations).

## Hints
- sum-without-carry = a ^ b; carry = (a & b) << 1.
- In Python, mask with 0xFFFFFFFF and convert back if the sign bit is set.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def get_sum(a, b):
    mask = 0xFFFFFFFF
    while b != 0:
        a, b = (a ^ b) & mask, ((a & b) << 1) & mask
    return a if a <= 0x7FFFFFFF else ~(a ^ mask)
```

### JavaScript
```javascript
function getSum(a, b) {
  while (b !== 0) {
    const carry = (a & b) << 1;
    a = a ^ b;
    b = carry;
  }
  return a;
}
```

### Java
```java
public int getSum(int a, int b) {
    while (b != 0) {
        int carry = (a & b) << 1;
        a = a ^ b;
        b = carry;
    }
    return a;
}
```

### C++
```cpp
int getSum(int a, int b) {
    while (b != 0) {
        unsigned carry = (unsigned)(a & b) << 1;  // unsigned avoids UB on overflow
        a = a ^ b;
        b = carry;
    }
    return a;
}
```

### C
```c
int getSum(int a, int b) {
    while (b != 0) {
        unsigned carry = (unsigned)(a & b) << 1;
        a = a ^ b;
        b = (int)carry;
    }
    return a;
}
```

### Rust
```rust
pub fn get_sum(a: i32, b: i32) -> i32 {
    let (mut a, mut b) = (a, b);
    while b != 0 {
        let carry = (a & b) << 1;
        a ^= b;
        b = carry;
    }
    a
}
```
