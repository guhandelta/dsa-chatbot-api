---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: bit-manipulation
fn_python: get_sum
fn_javascript: getSum
fn_typescript: getSum
fn_java: getSum
fn_cpp: get_sum
fn_c: get_sum
fn_rust: get_sum
fn_go: getSum
fn_csharp: GetSum
fn_ruby: get_sum
test_cases: [{"args": [0, 0], "expected": 0}, {"args": [13, 29], "expected": 42}, {"args": [-17, 4], "expected": -13}, {"args": [-9, -21], "expected": -30}, {"args": [0, -2147483648], "expected": -2147483648}, {"args": [2147483647, -2147483647], "expected": 0}, {"args": [1073741823, 1073741824], "expected": 2147483647}, {"args": [-100, 99], "expected": -1}, {"args": [65536, 65536], "expected": 131072}, {"args": [123456, 0], "expected": 123456}]
---
# Add Two Integers With Bit Operations Only — Medium — Bit Manipulation

## Problem
Given two signed 32-bit integers `a` and `b`, return their total. The total itself is guaranteed to fit in a signed 32-bit integer, so no overflow happens. The function must not use the addition or subtraction operators (`+`, `-`, and their compound forms `+=` and `-=`). Bitwise operators, shifts, comparisons, and loops are all allowed.

## Example
a = -4, b = 10 → 6

## Approach
Addition can be split into two parts. The XOR of `a` and `b` gives the sum of each bit column with the carries ignored. The AND of `a` and `b`, shifted left by one, gives the carries that each column pushes into the next column. Replace the pair `(a, b)` with `(a XOR b, (a AND b) << 1)` and repeat. Each round moves every carry one position higher, so after at most 32 rounds the carry is zero and `a` holds the answer. Negative values work with the same steps, because they are stored in two's complement form. Python and Ruby integers do not wrap at 32 bits, so they must mask each value to 32 bits and convert the result back to signed. The time is O(1), at most about 32 rounds, and the space is O(1).

## Hints
- Separate the sum into a carry-free part (XOR) and a carry part (AND shifted left).
- In Python or Ruby, keep both values masked to 32 bits during the loop, then turn the result back into a negative number if its top bit is set.

## Solutions
*Conventions: C++ and C use `int` with an `unsigned` carry so that overflow in the loop is well defined. Java code sits in `class Solution`. Rust uses `i32`. Go uses `int32`. C# uses `int`.*

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

### TypeScript
```typescript
function getSum(a: number, b: number): number {
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
class Solution {
    public int getSum(int a, int b) {
        while (b != 0) {
            int carry = (a & b) << 1;
            a = a ^ b;
            b = carry;
        }
        return a;
    }
}
```

### C++
```cpp
int get_sum(int a, int b) {
    while (b != 0) {
        unsigned carry = (unsigned)(a & b) << 1;
        a = a ^ b;
        b = (int)carry;
    }
    return a;
}
```

### C
```c
int get_sum(int a, int b) {
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
    let mut a = a;
    let mut b = b;
    while b != 0 {
        let carry = (a & b) << 1;
        a ^= b;
        b = carry;
    }
    a
}
```

### Go
```go
func getSum(a int32, b int32) int32 {
	for b != 0 {
		carry := (a & b) << 1
		a = a ^ b
		b = carry
	}
	return a
}
```

### C#
```csharp
public static class Solution {
    public static int GetSum(int a, int b) {
        while (b != 0) {
            int carry = (a & b) << 1;
            a = a ^ b;
            b = carry;
        }
        return a;
    }
}
```

### Ruby
```ruby
def get_sum(a, b)
  mask = 0xFFFFFFFF
  while b != 0
    a, b = (a ^ b) & mask, ((a & b) << 1) & mask
  end
  a <= 0x7FFFFFFF ? a : ~(a ^ mask)
end
```
