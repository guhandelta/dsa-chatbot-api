---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: dynamic-programming
fn_python: combination_sum4
fn_javascript: combinationSum4
test_cases: [{"args": [[1, 2, 3], 4], "expected": 7}, {"args": [[9], 3], "expected": 0}, {"args": [[1], 1], "expected": 1}, {"args": [[2, 3], 7], "expected": 3}, {"args": [[1, 2], 5], "expected": 8}, {"args": [[4, 2, 1], 32], "expected": 39882198}]
---
# Combination Sum IV (LC 377) — Medium — DP

## Problem
Given distinct positive integers and a target, count the number of ORDERED combinations (permutations) that sum to target.

## Example
nums = [1,2,3], target = 4 → 7

## Approach
dp[t] = number of sequences summing to t = sum over nums of dp[t - num]. Iterate targets outer, nums inner (order matters → permutations). Time O(target × n), space O(target).

## Hints
- Loop order distinguishes this from classic coin-change counting.
- dp[0] = 1 (the empty sequence).

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode. Counts can exceed 32-bit range mid-computation on other inputs; LC guarantees a 32-bit answer.*

### Python
```python
def combination_sum4(nums, target):
    dp = [1] + [0] * target
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]
```

### JavaScript
```javascript
function combinationSum4(nums, target) {
  const dp = new Array(target + 1).fill(0);
  dp[0] = 1;
  for (let t = 1; t <= target; t++)
    for (const x of nums)
      if (x <= t) dp[t] += dp[t - x];
  return dp[target];
}
```

### Java
```java
public int combinationSum4(int[] nums, int target) {
    int[] dp = new int[target + 1];
    dp[0] = 1;
    for (int t = 1; t <= target; t++)
        for (int x : nums)
            if (x <= t) dp[t] += dp[t - x];
    return dp[target];
}
```

### C++
```cpp
int combinationSum4(vector<int>& nums, int target) {
    vector<unsigned> dp(target + 1, 0);   // unsigned dodges intermediate overflow UB
    dp[0] = 1;
    for (int t = 1; t <= target; t++)
        for (int x : nums)
            if (x <= t) dp[t] += dp[t - x];
    return dp[target];
}
```

### C
```c
int combinationSum4(int* nums, int numsSize, int target) {
    unsigned* dp = calloc(target + 1, sizeof(unsigned));
    dp[0] = 1;
    for (int t = 1; t <= target; t++)
        for (int i = 0; i < numsSize; i++)
            if (nums[i] <= t) dp[t] += dp[t - nums[i]];
    int res = (int)dp[target];
    free(dp);
    return res;
}
```

### Rust
```rust
pub fn combination_sum4(nums: Vec<i32>, target: i32) -> i32 {
    let target = target as usize;
    let mut dp = vec![0u64; target + 1];
    dp[0] = 1;
    for t in 1..=target {
        for &x in &nums {
            let x = x as usize;
            if x <= t {
                dp[t] += dp[t - x];
            }
        }
    }
    dp[target] as i32
}
```
