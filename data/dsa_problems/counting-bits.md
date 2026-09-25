---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: bit-manipulation, dynamic-programming
fn_python: count_bits
fn_javascript: countBits
test_cases: [{"args": [2], "expected": [0, 1, 1]}, {"args": [5], "expected": [0, 1, 1, 2, 1, 2]}, {"args": [0], "expected": [0]}, {"args": [1], "expected": [0, 1]}, {"args": [8], "expected": [0, 1, 1, 2, 1, 2, 2, 3, 1]}, {"args": [3], "expected": [0, 1, 1, 2]}]
---
# Counting Bits (LC 338) — Easy — DP, Bit Manipulation

## Problem
For every i in [0, n], compute the number of 1 bits in i. Return the array. Aim for O(n).

## Example
n = 5 → [0,1,1,2,1,2]

## Approach
DP: bits(i) = bits(i >> 1) + (i & 1) — shifting right drops the last bit, which contributes (i & 1). Time O(n), space O(n) output.

## Hints
- Relate i to i >> 1 (already computed).
- Alternative recurrence: bits(i) = bits(i & (i-1)) + 1.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def count_bits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
```

### JavaScript
```javascript
function countBits(n) {
  const dp = new Array(n + 1).fill(0);
  for (let i = 1; i <= n; i++) dp[i] = dp[i >> 1] + (i & 1);
  return dp;
}
```

### Java
```java
public int[] countBits(int n) {
    int[] dp = new int[n + 1];
    for (int i = 1; i <= n; i++) dp[i] = dp[i >> 1] + (i & 1);
    return dp;
}
```

### C++
```cpp
vector<int> countBits(int n) {
    vector<int> dp(n + 1, 0);
    for (int i = 1; i <= n; i++) dp[i] = dp[i >> 1] + (i & 1);
    return dp;
}
```

### C
```c
int* countBits(int n, int* returnSize) {
    int* dp = calloc(n + 1, sizeof(int));
    *returnSize = n + 1;
    for (int i = 1; i <= n; i++) dp[i] = dp[i >> 1] + (i & 1);
    return dp;
}
```

### Rust
```rust
pub fn count_bits(n: i32) -> Vec<i32> {
    let n = n as usize;
    let mut dp = vec![0; n + 1];
    for i in 1..=n {
        dp[i] = dp[i >> 1] + (i as i32 & 1);
    }
    dp
}
```
