---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: bit-manipulation
fn_python: reverse_bits
fn_javascript: reverseBits
test_cases: [{"args": [43261596], "expected": 964176192}, {"args": [4294967293], "expected": 3221225471}, {"args": [0], "expected": 0}, {"args": [1], "expected": 2147483648}, {"args": [2147483648], "expected": 1}, {"args": [255], "expected": 4278190080}]
---
# Reverse Bits (LC 190) — Easy — Bit Manipulation

## Problem
Reverse the bits of a 32-bit unsigned integer and return the result. Inputs and outputs are integers in [0, 4294967295]. Java uses `long` to represent that unsigned range.

## Example
00000010100101000001111010011100 → 00111001011110000010100101000000

## Approach
Build the result bit by bit: 32 times, shift result left, OR in n's lowest bit, shift n right. Time O(1) (32 steps).

## Hints
- Take bits from one end, append to the other.
- In JavaScript, use >>> (unsigned shift) and >>> 0 on the result.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def reverse_bits(n):
    res = 0
    for _ in range(32):
        res = (res << 1) | (n & 1)
        n >>= 1
    return res
```

### JavaScript
```javascript
function reverseBits(n) {
  let res = 0;
  for (let i = 0; i < 32; i++) {
    res = (res << 1) | (n & 1);
    n >>>= 1;
  }
  return res >>> 0;
}
```

### Java
```java
public long reverseBits(long n) {
    long res = 0;
    for (int i = 0; i < 32; i++) {
        res = (res << 1) | (n & 1);
        n >>>= 1;
    }
    return res;
}
```

### C++
```cpp
uint32_t reverseBits(uint32_t n) {
    uint32_t res = 0;
    for (int i = 0; i < 32; i++) {
        res = (res << 1) | (n & 1);
        n >>= 1;
    }
    return res;
}
```

### C
```c
uint32_t reverseBits(uint32_t n) {
    uint32_t res = 0;
    for (int i = 0; i < 32; i++) {
        res = (res << 1) | (n & 1);
        n >>= 1;
    }
    return res;
}
```

### Rust
```rust
pub fn reverse_bits(n: u32) -> u32 {
    n.reverse_bits()   // or the manual 32-step shift loop
}
```
