---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: bit-manipulation
fn_python: hamming_weight
fn_javascript: hammingWeight
fn_typescript: hammingWeight
fn_java: hammingWeight
fn_cpp: hammingWeight
fn_c: hammingWeight
fn_rust: hamming_weight
fn_go: hammingWeight
fn_csharp: HammingWeight
fn_ruby: hamming_weight
test_cases: [{"args": [0], "expected": 0}, {"args": [4294967295], "expected": 32}, {"args": [2], "expected": 1}, {"args": [6], "expected": 2}, {"args": [1024], "expected": 1}, {"args": [3000000000], "expected": 12}, {"args": [65535], "expected": 16}, {"args": [1431655765], "expected": 16}, {"args": [2147483648], "expected": 1}, {"args": [43690], "expected": 8}]
---
# Count the Set Bits in a Word — Easy — Bit Manipulation

## Problem
Given an integer `value` in the range 0 through 4294967295, read it as an unsigned 32-bit number and return how many bits of its binary representation are 1. Java receives the input as a `long` so that the full unsigned range is representable.

## Example
value = 100 (binary 1100100) → 3

## Approach
Use the fact that subtracting 1 from a number flips its lowest set bit and every bit below it. Doing a bitwise AND of the number with one less than itself therefore removes exactly one set bit. Repeat until the value becomes zero and count the steps. The loop runs once per set bit, so the time is O(k), where k is the number of set bits.

## Hints
- What does value AND (value - 1) do to the lowest set bit?
- Most languages also provide a built-in bit-count function, but the loop is the point of this exercise.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java methods sit inside `class Solution` with `import java.util.*;`. Rust functions are free functions.*

### Python
```python
def hamming_weight(value):
    ones = 0
    while value:
        value &= value - 1
        ones += 1
    return ones
```

### JavaScript
```javascript
function hammingWeight(value) {
  let ones = 0;
  while (value !== 0) {
    value &= value - 1;
    ones++;
  }
  return ones;
}
```

### TypeScript
```typescript
function hammingWeight(value: number): number {
  let ones = 0;
  while (value !== 0) {
    value &= value - 1;
    ones++;
  }
  return ones;
}
```

### Java
```java
public int hammingWeight(long value) {
    int ones = 0;
    while (value != 0) {
        value &= value - 1;
        ones++;
    }
    return ones;
}
```

### C++
```cpp
int hammingWeight(uint32_t value) {
    int ones = 0;
    while (value) {
        value &= value - 1;
        ones++;
    }
    return ones;
}
```

### C
```c
int hammingWeight(unsigned int value) {
    int ones = 0;
    while (value) {
        value &= value - 1;
        ones++;
    }
    return ones;
}
```

### Rust
```rust
pub fn hamming_weight(value: i64) -> i64 {
    let mut v = value;
    let mut ones = 0;
    while v != 0 {
        v &= v - 1;
        ones += 1;
    }
    ones
}
```

### Go
```go
func hammingWeight(value uint32) int {
	ones := 0
	for value != 0 {
		value &= value - 1
		ones++
	}
	return ones
}
```

### C#
```csharp
public static int HammingWeight(uint value)
{
    int ones = 0;
    while (value != 0)
    {
        value &= value - 1;
        ones++;
    }
    return ones;
}
```

### Ruby
```ruby
def hamming_weight(value)
  ones = 0
  while value != 0
    value &= value - 1
    ones += 1
  end
  ones
end
```
