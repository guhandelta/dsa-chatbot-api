---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: arrays, dynamic-programming
fn_python: max_product
fn_javascript: maxProduct
test_cases: [{"args": [[2, 3, -2, 4]], "expected": 6}, {"args": [[-2, 0, -1]], "expected": 0}, {"args": [[-2]], "expected": -2}, {"args": [[0, 2]], "expected": 2}, {"args": [[-2, 3, -4]], "expected": 24}, {"args": [[3, -1, 4]], "expected": 4}]
---
# Maximum Product Subarray (LC 152) — Medium — Array, DP

## Problem
Find the contiguous subarray with the largest product and return that product.

## Example
[2,3,-2,4] → 6 ([2,3])

## Approach
A negative number flips the largest product into the smallest and vice versa, so track BOTH the max and min product ending at each index. Time O(n), space O(1).

## Hints
- Why isn't Kadane's alone enough? Negatives.
- When nums[i] < 0, swap the running max and min before updating.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def max_product(nums):
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        if x < 0:
            cur_max, cur_min = cur_min, cur_max
        cur_max = max(x, cur_max * x)
        cur_min = min(x, cur_min * x)
        best = max(best, cur_max)
    return best
```

### JavaScript
```javascript
function maxProduct(nums) {
  let best = nums[0], curMax = nums[0], curMin = nums[0];
  for (let i = 1; i < nums.length; i++) {
    const x = nums[i];
    if (x < 0) [curMax, curMin] = [curMin, curMax];
    curMax = Math.max(x, curMax * x);
    curMin = Math.min(x, curMin * x);
    best = Math.max(best, curMax);
  }
  return best;
}
```

### Java
```java
public int maxProduct(int[] nums) {
    int best = nums[0], curMax = nums[0], curMin = nums[0];
    for (int i = 1; i < nums.length; i++) {
        int x = nums[i];
        if (x < 0) { int t = curMax; curMax = curMin; curMin = t; }
        curMax = Math.max(x, curMax * x);
        curMin = Math.min(x, curMin * x);
        best = Math.max(best, curMax);
    }
    return best;
}
```

### C++
```cpp
int maxProduct(vector<int>& nums) {
    int best = nums[0], curMax = nums[0], curMin = nums[0];
    for (size_t i = 1; i < nums.size(); i++) {
        int x = nums[i];
        if (x < 0) swap(curMax, curMin);
        curMax = max(x, curMax * x);
        curMin = min(x, curMin * x);
        best = max(best, curMax);
    }
    return best;
}
```

### C
```c
int maxProduct(int* nums, int numsSize) {
    int best = nums[0], curMax = nums[0], curMin = nums[0];
    for (int i = 1; i < numsSize; i++) {
        int x = nums[i];
        if (x < 0) { int t = curMax; curMax = curMin; curMin = t; }
        curMax = x > curMax * x ? x : curMax * x;
        curMin = x < curMin * x ? x : curMin * x;
        if (curMax > best) best = curMax;
    }
    return best;
}
```

### Rust
```rust
pub fn max_product(nums: Vec<i32>) -> i32 {
    let (mut best, mut cur_max, mut cur_min) = (nums[0], nums[0], nums[0]);
    for &x in &nums[1..] {
        if x < 0 {
            std::mem::swap(&mut cur_max, &mut cur_min);
        }
        cur_max = x.max(cur_max * x);
        cur_min = x.min(cur_min * x);
        best = best.max(cur_max);
    }
    best
}
```
