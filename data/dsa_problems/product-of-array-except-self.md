---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: arrays, prefix-sum
fn_python: product_except_self
fn_javascript: productExceptSelf
test_cases: [{"args": [[1, 2, 3, 4]], "expected": [24, 12, 8, 6]}, {"args": [[-1, 1, 0, -3, 3]], "expected": [0, 0, 9, 0, 0]}, {"args": [[2, 3]], "expected": [3, 2]}, {"args": [[1, 1, 1]], "expected": [1, 1, 1]}, {"args": [[5, 0]], "expected": [0, 5]}, {"args": [[-1, -2, -3]], "expected": [6, 3, 2]}]
---
# Product of Array Except Self (LC 238) — Medium — Array, Prefix Product

## Problem
Return an array `ans` where `ans[i]` is the product of every element of `nums` except `nums[i]`. No division; O(n) time required.

## Example
[1,2,3,4] → [24,12,8,6]

## Approach
Two sweeps: first store the product of everything to the LEFT of i; then sweep right-to-left multiplying in the running product of everything to the RIGHT. Time O(n), space O(1) beyond the output.

## Hints
- ans[i] = (product of prefix before i) × (product of suffix after i).
- The output array can hold the prefix products; carry the suffix in one variable.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def product_except_self(nums):
    n = len(nums)
    ans = [1] * n
    for i in range(1, n):
        ans[i] = ans[i - 1] * nums[i - 1]
    right = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= right
        right *= nums[i]
    return ans
```

### JavaScript
```javascript
function productExceptSelf(nums) {
  const n = nums.length, ans = new Array(n).fill(1);
  for (let i = 1; i < n; i++) ans[i] = ans[i - 1] * nums[i - 1];
  let right = 1;
  for (let i = n - 1; i >= 0; i--) {
    ans[i] *= right;
    right *= nums[i];
  }
  return ans;
}
```

### Java
```java
public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] ans = new int[n];
    ans[0] = 1;
    for (int i = 1; i < n; i++) ans[i] = ans[i - 1] * nums[i - 1];
    int right = 1;
    for (int i = n - 1; i >= 0; i--) {
        ans[i] *= right;
        right *= nums[i];
    }
    return ans;
}
```

### C++
```cpp
vector<int> productExceptSelf(vector<int>& nums) {
    int n = nums.size();
    vector<int> ans(n, 1);
    for (int i = 1; i < n; i++) ans[i] = ans[i - 1] * nums[i - 1];
    int right = 1;
    for (int i = n - 1; i >= 0; i--) {
        ans[i] *= right;
        right *= nums[i];
    }
    return ans;
}
```

### C
```c
int* productExceptSelf(int* nums, int numsSize, int* returnSize) {
    int* ans = malloc(numsSize * sizeof(int));
    *returnSize = numsSize;
    ans[0] = 1;
    for (int i = 1; i < numsSize; i++) ans[i] = ans[i - 1] * nums[i - 1];
    int right = 1;
    for (int i = numsSize - 1; i >= 0; i--) {
        ans[i] *= right;
        right *= nums[i];
    }
    return ans;
}
```

### Rust
```rust
pub fn product_except_self(nums: Vec<i32>) -> Vec<i32> {
    let n = nums.len();
    let mut ans = vec![1; n];
    for i in 1..n {
        ans[i] = ans[i - 1] * nums[i - 1];
    }
    let mut right = 1;
    for i in (0..n).rev() {
        ans[i] *= right;
        right *= nums[i];
    }
    ans
}
```
