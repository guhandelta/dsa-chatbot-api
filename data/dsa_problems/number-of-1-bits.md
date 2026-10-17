---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: bit-manipulation
fn_python: hamming_weight
fn_javascript: hammingWeight
test_cases: [{"args": [11], "expected": 3}, {"args": [128], "expected": 1}, {"args": [0], "expected": 0}, {"args": [4294967293], "expected": 31}, {"args": [1], "expected": 1}, {"args": [255], "expected": 8}]
---
# Number of 1 Bits (LC 191) — Easy — Bit Manipulation

## Problem
Return the number of set bits (Hamming weight) in the binary representation of an unsigned 32-bit integer in [0, 4294967295]. Java uses `long` to represent the unsigned input.

## Example
n = 11 (1011) → 3

## Approach
n & (n - 1) clears the lowest set bit; loop until zero, counting iterations. Runs once per set bit. Time O(k) where k = popcount.

## Hints
- Subtracting 1 flips the lowest set bit and everything below it.
- Most languages also expose a builtin popcount.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
```

### JavaScript
```javascript
function hammingWeight(n) {
  let count = 0;
  while (n !== 0) {
    n &= n - 1;
    count++;
  }
  return count;
}
```

### Java
```java
public int hammingWeight(long n) {
    int count = 0;
    while (n != 0) {
        n &= n - 1;
        count++;
    }
    return count;
}
```

### C++
```cpp
int hammingWeight(uint32_t n) {
    int count = 0;
    while (n) {
        n &= n - 1;
        count++;
    }
    return count;
}
```

### C
```c
int hammingWeight(uint32_t n) {
    int count = 0;
    while (n) {
        n &= n - 1;
        count++;
    }
    return count;
}
```

### Rust
```rust
pub fn hamming_weight(n: u32) -> i32 {
    n.count_ones() as i32   // or the n &= n-1 loop
}
```
