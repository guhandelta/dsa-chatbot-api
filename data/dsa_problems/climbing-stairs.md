---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: dynamic-programming
fn_python: climb_stairs
fn_javascript: climbStairs
test_cases: [{"args": [2], "expected": 2}, {"args": [3], "expected": 3}, {"args": [1], "expected": 1}, {"args": [5], "expected": 8}, {"args": [10], "expected": 89}, {"args": [45], "expected": 1836311903}]
---
# Climbing Stairs (LC 70) — Easy — DP

## Problem
You climb a staircase of n steps taking 1 or 2 steps at a time. How many distinct ways can you reach the top?

## Example
n = 3 → 3 (1+1+1, 1+2, 2+1)

## Approach
ways(n) = ways(n-1) + ways(n-2) — the Fibonacci recurrence. Iterate with two variables. Time O(n), space O(1).

## Hints
- The last move was either a 1-step or a 2-step.
- No memo table needed; keep only the previous two values.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def climb_stairs(n):
    a, b = 1, 1            # ways(0), ways(1)
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

### JavaScript
```javascript
function climbStairs(n) {
  let a = 1, b = 1;
  for (let i = 0; i < n - 1; i++) [a, b] = [b, a + b];
  return b;
}
```

### Java
```java
public int climbStairs(int n) {
    int a = 1, b = 1;
    for (int i = 0; i < n - 1; i++) {
        int next = a + b;
        a = b;
        b = next;
    }
    return b;
}
```

### C++
```cpp
int climbStairs(int n) {
    int a = 1, b = 1;
    for (int i = 0; i < n - 1; i++) {
        int next = a + b;
        a = b;
        b = next;
    }
    return b;
}
```

### C
```c
int climbStairs(int n) {
    int a = 1, b = 1;
    for (int i = 0; i < n - 1; i++) {
        int next = a + b;
        a = b;
        b = next;
    }
    return b;
}
```

### Rust
```rust
pub fn climb_stairs(n: i32) -> i32 {
    let (mut a, mut b) = (1, 1);
    for _ in 0..n - 1 {
        let next = a + b;
        a = b;
        b = next;
    }
    b
}
```
