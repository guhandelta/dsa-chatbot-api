---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: bit-manipulation, math
fn_python: missing_number
fn_javascript: missingNumber
test_cases: [{"args": [[3, 0, 1]], "expected": 2}, {"args": [[0, 1]], "expected": 2}, {"args": [[9, 6, 4, 2, 3, 5, 7, 0, 1]], "expected": 8}, {"args": [[0]], "expected": 1}, {"args": [[1]], "expected": 0}, {"args": [[0, 2]], "expected": 1}]
---
# Missing Number (LC 268) — Easy — Bit Manipulation / Math

## Problem
Array `nums` contains n distinct numbers from the range [0, n]; exactly one number in the range is missing. Return it.

## Example
[3,0,1] → 2

## Approach
XOR all indices 0..n with all values: pairs cancel, leaving the missing number. (Or use the sum formula n(n+1)/2 minus the array sum.) Time O(n), space O(1).

## Hints
- x ^ x = 0 and XOR is order-independent.
- Sum formula works too but watch overflow in 32-bit languages.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def missing_number(nums):
    res = len(nums)
    for i, x in enumerate(nums):
        res ^= i ^ x
    return res
```

### JavaScript
```javascript
function missingNumber(nums) {
  let res = nums.length;
  for (let i = 0; i < nums.length; i++) res ^= i ^ nums[i];
  return res;
}
```

### Java
```java
public int missingNumber(int[] nums) {
    int res = nums.length;
    for (int i = 0; i < nums.length; i++) res ^= i ^ nums[i];
    return res;
}
```

### C++
```cpp
int missingNumber(vector<int>& nums) {
    int res = nums.size();
    for (int i = 0; i < (int)nums.size(); i++) res ^= i ^ nums[i];
    return res;
}
```

### C
```c
int missingNumber(int* nums, int numsSize) {
    int res = numsSize;
    for (int i = 0; i < numsSize; i++) res ^= i ^ nums[i];
    return res;
}
```

### Rust
```rust
pub fn missing_number(nums: Vec<i32>) -> i32 {
    let mut res = nums.len() as i32;
    for (i, &x) in nums.iter().enumerate() {
        res ^= i as i32 ^ x;
    }
    res
}
```
