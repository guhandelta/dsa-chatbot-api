---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: binary-search
fn_python: search
fn_javascript: search
test_cases: [{"args": [[-1, 0, 3, 5, 9, 12], 9], "expected": 4}, {"args": [[-1, 0, 3, 5, 9, 12], 2], "expected": -1}, {"args": [[5], 5], "expected": 0}, {"args": [[5], -5], "expected": -1}, {"args": [[1, 2], 2], "expected": 1}, {"args": [[1, 2, 3, 4, 5], 1], "expected": 0}]
---
# Binary Search (LC 704) — Easy — Binary Search

## Problem
Given a sorted (ascending) array of distinct integers and a target, return its index or -1. Required runtime: O(log n).

## Example
nums = [-1,0,3,5,9,12], target = 9 → 4

## Approach
Maintain a window [lo, hi]; compare the middle with the target and discard half each step. Time O(log n), space O(1).

## Hints
- Use mid = lo + (hi - lo) / 2 to avoid overflow in fixed-width languages.
- Loop while lo <= hi so the last candidate is examined.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### JavaScript
```javascript
function search(nums, target) {
  let lo = 0, hi = nums.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (nums[mid] === target) return mid;
    if (nums[mid] < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}
```

### Java
```java
public int search(int[] nums, int target) {
    int lo = 0, hi = nums.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### C++
```cpp
int search(vector<int>& nums, int target) {
    int lo = 0, hi = nums.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### C
```c
int search(int* nums, int numsSize, int target) {
    int lo = 0, hi = numsSize - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### Rust
```rust
pub fn search(nums: Vec<i32>, target: i32) -> i32 {
    let (mut lo, mut hi) = (0i32, nums.len() as i32 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        let v = nums[mid as usize];
        if v == target { return mid; }
        if v < target { lo = mid + 1; } else { hi = mid - 1; }
    }
    -1
}
```
