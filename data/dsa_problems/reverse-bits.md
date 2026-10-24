---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: bit-manipulation
fn_python: reverse_bits
fn_javascript: reverseBits
fn_typescript: reverseBits
fn_java: reverseBits
fn_cpp: reverse_bits
fn_c: reverse_bits
fn_rust: reverse_bits
fn_go: reverseBits
fn_csharp: ReverseBits
fn_ruby: reverse_bits
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 2147483648}, {"args": [2], "expected": 1073741824}, {"args": [3], "expected": 3221225472}, {"args": [6], "expected": 1610612736}, {"args": [65536], "expected": 32768}, {"args": [2147483648], "expected": 1}, {"args": [1431655765], "expected": 2863311530}, {"args": [4294967294], "expected": 2147483647}, {"args": [4294967295], "expected": 4294967295}]
---
# Mirror the Bit Order of a Word — Easy — Bit Manipulation

## Problem
Think of an unsigned 32-bit integer `n` as a row of 32 bit positions, numbered 0 (least significant) to 31 (most significant). Return the integer whose bit at position `i` equals the bit of `n` at position `31 - i`, for every `i` from 0 to 31.

The input and the output are both whole numbers in the range [0, 4294967295]. Java has no unsigned int, so Java receives and returns a `long` that holds such a value.

## Example
n = 6 (bits 1 and 2 are set) → 1610612736 (bits 30 and 29 are set)

## Approach
Build the answer from the low end. Repeat 32 times: shift the answer left by one, copy the lowest bit of `n` into the lowest bit of the answer, then shift `n` right by one. After 32 rounds every bit of `n` has been copied to its mirrored position. The work is fixed at 32 steps, so the time is O(1) and the space is O(1).

## Hints
- Read the input from its lowest bit while you write the output from its lowest bit upward; the two directions are opposite.
- Use an unsigned right shift (or mask the result) so that a set top bit never fills the high positions with sign bits.

## Solutions
*Conventions: C and C++ take a `uint32_t` from `<stdint.h>`; the C++ result is returned as `unsigned long long` (same value, which is below 2^32). Java code sits in `class Solution`. Rust works on 64-bit values that hold the 32-bit input and output. C# uses `uint`.*

### Python
```python
def reverse_bits(n):
    out = 0
    for _ in range(32):
        out = (out << 1) | (n & 1)
        n >>= 1
    return out
```

### JavaScript
```javascript
function reverseBits(n) {
  let out = 0;
  for (let i = 0; i < 32; i++) {
    out = (out << 1) | (n & 1);
    n >>>= 1;
  }
  return out >>> 0;
}
```

### TypeScript
```typescript
function reverseBits(n: number): number {
  let out = 0;
  for (let i = 0; i < 32; i++) {
    out = (out << 1) | (n & 1);
    n >>>= 1;
  }
  return out >>> 0;
}
```

### Java
```java
class Solution {
    public long reverseBits(long n) {
        long out = 0;
        for (int i = 0; i < 32; i++) {
            out = (out << 1) | (n & 1);
            n >>>= 1;
        }
        return out;
    }
}
```

### C++
```cpp
#include <stdint.h>

unsigned long long reverse_bits(uint32_t n) {
    unsigned long long out = 0;
    for (int i = 0; i < 32; i++) {
        out = (out << 1) | (n & 1u);
        n >>= 1;
    }
    return out;
}
```

### C
```c
#include <stdint.h>

uint32_t reverse_bits(uint32_t n) {
    uint32_t out = 0;
    for (int i = 0; i < 32; i++) {
        out = (out << 1) | (n & 1u);
        n >>= 1;
    }
    return out;
}
```

### Rust
```rust
pub fn reverse_bits(n: i64) -> i64 {
    let mut n = n as u64;
    let mut out: u64 = 0;
    for _ in 0..32 {
        out = (out << 1) | (n & 1);
        n >>= 1;
    }
    out as i64
}
```

### Go
```go
func reverseBits(n uint32) uint32 {
	var out uint32
	for i := 0; i < 32; i++ {
		out = out<<1 | n&1
		n >>= 1
	}
	return out
}
```

### C#
```csharp
public static class Solution {
    public static uint ReverseBits(uint n) {
        uint outBits = 0;
        for (int i = 0; i < 32; i++) {
            outBits = (outBits << 1) | (n & 1u);
            n >>= 1;
        }
        return outBits;
    }
}
```

### Ruby
```ruby
def reverse_bits(n)
  out = 0
  32.times do
    out = (out << 1) | (n & 1)
    n >>= 1
  end
  out
end
```
