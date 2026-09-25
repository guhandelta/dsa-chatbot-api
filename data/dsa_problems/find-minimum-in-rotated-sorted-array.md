---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: binary-search
fn_python: find_min
fn_javascript: findMin
test_cases: [{"args": [[3, 4, 5, 1, 2]], "expected": 1}, {"args": [[4, 5, 6, 7, 0, 1, 2]], "expected": 0}, {"args": [[11, 13, 15, 17]], "expected": 11}, {"args": [[1]], "expected": 1}, {"args": [[2, 1]], "expected": 1}, {"args": [[5, 1, 2, 3, 4]], "expected": 1}]
---
# Find Minimum in Rotated Sorted Array (LC 153) — Medium — Binary Search

## Problem
A sorted array of unique values was rotated some number of times. Find the minimum element in O(log n).

## Example
[3,4,5,1,2] → 1

## Approach
Binary search: if nums[mid] > nums[hi], the minimum lies strictly right of mid; otherwise it's at mid or left. Time O(log n), space O(1).

## Hints
- Compare mid against the RIGHT endpoint, not the left.
- Loop while lo < hi; lo lands on the minimum.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
```

### JavaScript
```javascript
function findMin(nums) {
  let lo = 0, hi = nums.length - 1;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (nums[mid] > nums[hi]) lo = mid + 1;
    else hi = mid;
  }
  return nums[lo];
}
```

### Java
```java
public int findMin(int[] nums) {
    int lo = 0, hi = nums.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### C++
```cpp
int findMin(vector<int>& nums) {
    int lo = 0, hi = nums.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### C
```c
int findMin(int* nums, int numsSize) {
    int lo = 0, hi = numsSize - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### Rust
```rust
pub fn find_min(nums: Vec<i32>) -> i32 {
    let (mut lo, mut hi) = (0usize, nums.len() - 1);
    while lo < hi {
        let mid = (lo + hi) / 2;
        if nums[mid] > nums[hi] { lo = mid + 1; } else { hi = mid; }
    }
    nums[lo]
}
```
