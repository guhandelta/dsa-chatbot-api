---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: binary-search, dynamic-programming
fn_python: length_of_lis
fn_javascript: lengthOfLIS
test_cases: [{"args": [[10, 9, 2, 5, 3, 7, 101, 18]], "expected": 4}, {"args": [[0, 1, 0, 3, 2, 3]], "expected": 4}, {"args": [[7, 7, 7, 7, 7]], "expected": 1}, {"args": [[1]], "expected": 1}, {"args": [[3, 2, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}]
---
# Longest Increasing Subsequence (LC 300) — Medium — DP, Binary Search

## Problem
Return the length of the longest strictly increasing subsequence of `nums` (elements need not be contiguous).

## Example
[10,9,2,5,3,7,101,18] → 4 ([2,3,7,101])

## Approach
Patience sorting: keep `tails`, where tails[k] is the smallest possible tail of an increasing subsequence of length k+1. For each x, binary-search the first tail >= x and replace it (or append). Length of tails is the answer. Time O(n log n), space O(n). (Classic O(n^2) DP also acceptable.)

## Hints
- tails stays sorted, enabling binary search.
- Replacing keeps lengths intact while improving future extensibility.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
import bisect

def length_of_lis(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

### JavaScript
```javascript
function lengthOfLIS(nums) {
  const tails = [];
  for (const x of nums) {
    let lo = 0, hi = tails.length;
    while (lo < hi) {                 // lower_bound
      const mid = (lo + hi) >> 1;
      if (tails[mid] < x) lo = mid + 1;
      else hi = mid;
    }
    tails[lo] = x;                    // appends when lo === length
  }
  return tails.length;
}
```

### Java
```java
public int lengthOfLIS(int[] nums) {
    int[] tails = new int[nums.length];
    int size = 0;
    for (int x : nums) {
        int lo = 0, hi = size;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (tails[mid] < x) lo = mid + 1;
            else hi = mid;
        }
        tails[lo] = x;
        if (lo == size) size++;
    }
    return size;
}
```

### C++
```cpp
int lengthOfLIS(vector<int>& nums) {
    vector<int> tails;
    for (int x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x);
        else *it = x;
    }
    return tails.size();
}
```

### C
```c
int lengthOfLIS(int* nums, int numsSize) {
    int* tails = malloc(numsSize * sizeof(int));
    int size = 0;
    for (int i = 0; i < numsSize; i++) {
        int x = nums[i], lo = 0, hi = size;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (tails[mid] < x) lo = mid + 1;
            else hi = mid;
        }
        tails[lo] = x;
        if (lo == size) size++;
    }
    free(tails);
    return size;
}
```

### Rust
```rust
pub fn length_of_lis(nums: Vec<i32>) -> i32 {
    let mut tails: Vec<i32> = Vec::new();
    for x in nums {
        let i = tails.partition_point(|&t| t < x);
        if i == tails.len() {
            tails.push(x);
        } else {
            tails[i] = x;
        }
    }
    tails.len() as i32
}
```
