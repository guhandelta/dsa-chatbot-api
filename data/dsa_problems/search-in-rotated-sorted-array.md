---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: binary-search
fn_python: search
fn_javascript: search
test_cases: [{"args": [[4, 5, 6, 7, 0, 1, 2], 0], "expected": 4}, {"args": [[4, 5, 6, 7, 0, 1, 2], 3], "expected": -1}, {"args": [[1], 0], "expected": -1}, {"args": [[1], 1], "expected": 0}, {"args": [[5, 1, 3], 3], "expected": 2}, {"args": [[1, 3], 3], "expected": 1}]
---
# Search in Rotated Sorted Array (LC 33) — Medium — Binary Search

## Problem
Search for `target` in a rotated sorted array of distinct values; return its index or -1, in O(log n).

## Example
nums = [4,5,6,7,0,1,2], target = 0 → 4

## Approach
At every mid, one half is sorted. Determine which half is sorted, check whether target lies in that half's range, and discard the other half. Time O(log n), space O(1).

## Hints
- nums[lo] <= nums[mid] means the left half is sorted.
- Range-check target against the sorted half's endpoints to decide direction.

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
        if nums[lo] <= nums[mid]:            # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                # right half sorted
            if nums[mid] < target <= nums[hi]:
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
    if (nums[lo] <= nums[mid]) {
      if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
      else lo = mid + 1;
    } else {
      if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
      else hi = mid - 1;
    }
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
        if (nums[lo] <= nums[mid]) {
            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
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
        if (nums[lo] <= nums[mid]) {
            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
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
        if (nums[lo] <= nums[mid]) {
            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {
            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}
```

### Rust
```rust
pub fn search(nums: Vec<i32>, target: i32) -> i32 {
    let (mut lo, mut hi) = (0i32, nums.len() as i32 - 1);
    while lo <= hi {
        let mid = (lo + hi) / 2;
        let (l, m, h) = (nums[lo as usize], nums[mid as usize], nums[hi as usize]);
        if m == target { return mid; }
        if l <= m {
            if l <= target && target < m { hi = mid - 1; } else { lo = mid + 1; }
        } else {
            if m < target && target <= h { lo = mid + 1; } else { hi = mid - 1; }
        }
    }
    -1
}
```
