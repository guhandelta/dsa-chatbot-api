---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: arrays, dynamic-programming, kadane
fn_python: max_sub_array
fn_javascript: maxSubArray
test_cases: [{"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6}, {"args": [[1]], "expected": 1}, {"args": [[5, 4, -1, 7, 8]], "expected": 23}, {"args": [[-1]], "expected": -1}, {"args": [[-2, -1]], "expected": -1}, {"args": [[0, 0, 0]], "expected": 0}]
---
# Maximum Subarray (LC 53) — Medium — Array, Kadane's Algorithm / DP

## Problem
Find the contiguous subarray (at least one element) with the largest sum and return that sum.

## Example
[-2,1,-3,4,-1,2,1,-5,4] → 6 (subarray [4,-1,2,1])

## Approach
Kadane's: keep a running sum; if it drops below zero it can only hurt, so reset to the current element. Track the best seen. Time O(n), space O(1).

## Hints
- A negative running prefix never helps a future subarray.
- cur = max(x, cur + x); best = max(best, cur).

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def max_sub_array(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

### JavaScript
```javascript
function maxSubArray(nums) {
  let best = nums[0], cur = nums[0];
  for (let i = 1; i < nums.length; i++) {
    cur = Math.max(nums[i], cur + nums[i]);
    best = Math.max(best, cur);
  }
  return best;
}
```

### Java
```java
public int maxSubArray(int[] nums) {
    int best = nums[0], cur = nums[0];
    for (int i = 1; i < nums.length; i++) {
        cur = Math.max(nums[i], cur + nums[i]);
        best = Math.max(best, cur);
    }
    return best;
}
```

### C++
```cpp
int maxSubArray(vector<int>& nums) {
    int best = nums[0], cur = nums[0];
    for (size_t i = 1; i < nums.size(); i++) {
        cur = max(nums[i], cur + nums[i]);
        best = max(best, cur);
    }
    return best;
}
```

### C
```c
int maxSubArray(int* nums, int numsSize) {
    int best = nums[0], cur = nums[0];
    for (int i = 1; i < numsSize; i++) {
        cur = nums[i] > cur + nums[i] ? nums[i] : cur + nums[i];
        if (cur > best) best = cur;
    }
    return best;
}
```

### Rust
```rust
pub fn max_sub_array(nums: Vec<i32>) -> i32 {
    let (mut best, mut cur) = (nums[0], nums[0]);
    for &x in &nums[1..] {
        cur = x.max(cur + x);
        best = best.max(cur);
    }
    best
}
```
