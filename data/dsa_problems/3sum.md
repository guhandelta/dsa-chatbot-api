---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
comparison: unordered_nested
algorithms: arrays, sorting, two-pointers
fn_python: three_sum
fn_javascript: threeSum
test_cases: [{"args": [[-1, 0, 1, 2, -1, -4]], "expected": [[-1, -1, 2], [-1, 0, 1]]}, {"args": [[0, 1, 1]], "expected": []}, {"args": [[0, 0, 0]], "expected": [[0, 0, 0]]}, {"args": [[-2, 0, 1, 1, 2]], "expected": [[-2, 0, 2], [-2, 1, 1]]}, {"args": [[1, 2, -2, -1]], "expected": []}, {"args": [[0, 0, 0, 0]], "expected": [[0, 0, 0]]}]
---
# 3Sum (LC 15) — Medium — Array, Two Pointers, Sorting

## Problem
Return all unique triplets [a,b,c] from `nums` with a + b + c = 0. The result must not contain duplicate triplets.

## Example
[-1,0,1,2,-1,-4] → [[-1,-1,2],[-1,0,1]]

## Approach
Sort, then for each index i run a two-pointer scan on the remainder looking for pairs summing to -nums[i]. Skip duplicate values at every position. Time O(n^2), space O(1) beyond output.

## Hints
- Sorting makes both the two-pointer scan and duplicate-skipping possible.
- After a match, advance BOTH pointers past any equal neighbors.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def three_sum(nums):
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                res.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                hi -= 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                while lo < hi and nums[hi] == nums[hi + 1]:
                    hi -= 1
    return res
```

### JavaScript
```javascript
function threeSum(nums) {
  nums.sort((a, b) => a - b);
  const res = [];
  for (let i = 0; i < nums.length - 2; i++) {
    if (nums[i] > 0) break;
    if (i > 0 && nums[i] === nums[i - 1]) continue;
    let lo = i + 1, hi = nums.length - 1;
    while (lo < hi) {
      const s = nums[i] + nums[lo] + nums[hi];
      if (s < 0) lo++;
      else if (s > 0) hi--;
      else {
        res.push([nums[i], nums[lo], nums[hi]]);
        lo++; hi--;
        while (lo < hi && nums[lo] === nums[lo - 1]) lo++;
        while (lo < hi && nums[hi] === nums[hi + 1]) hi--;
      }
    }
  }
  return res;
}
```

### Java
```java
public List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    List<List<Integer>> res = new ArrayList<>();
    for (int i = 0; i < nums.length - 2; i++) {
        if (nums[i] > 0) break;
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int lo = i + 1, hi = nums.length - 1;
        while (lo < hi) {
            int s = nums[i] + nums[lo] + nums[hi];
            if (s < 0) lo++;
            else if (s > 0) hi--;
            else {
                res.add(Arrays.asList(nums[i], nums[lo], nums[hi]));
                lo++; hi--;
                while (lo < hi && nums[lo] == nums[lo - 1]) lo++;
                while (lo < hi && nums[hi] == nums[hi + 1]) hi--;
            }
        }
    }
    return res;
}
```

### C++
```cpp
vector<vector<int>> threeSum(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    vector<vector<int>> res;
    int n = nums.size();
    for (int i = 0; i < n - 2; i++) {
        if (nums[i] > 0) break;
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int lo = i + 1, hi = n - 1;
        while (lo < hi) {
            int s = nums[i] + nums[lo] + nums[hi];
            if (s < 0) lo++;
            else if (s > 0) hi--;
            else {
                res.push_back({nums[i], nums[lo], nums[hi]});
                lo++; hi--;
                while (lo < hi && nums[lo] == nums[lo - 1]) lo++;
                while (lo < hi && nums[hi] == nums[hi + 1]) hi--;
            }
        }
    }
    return res;
}
```

### C
```c
static int cmp_int(const void* a, const void* b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}
/* LeetCode C signature: returns array of triplets. */
int** threeSum(int* nums, int numsSize, int* returnSize, int** returnColumnSizes) {
    qsort(nums, numsSize, sizeof(int), cmp_int);
    int cap = 64, count = 0;
    int** res = malloc(cap * sizeof(int*));
    *returnColumnSizes = malloc(cap * sizeof(int));
    for (int i = 0; i < numsSize - 2; i++) {
        if (nums[i] > 0) break;
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int lo = i + 1, hi = numsSize - 1;
        while (lo < hi) {
            int s = nums[i] + nums[lo] + nums[hi];
            if (s < 0) lo++;
            else if (s > 0) hi--;
            else {
                if (count == cap) {
                    cap *= 2;
                    res = realloc(res, cap * sizeof(int*));
                    *returnColumnSizes = realloc(*returnColumnSizes, cap * sizeof(int));
                }
                int* t = malloc(3 * sizeof(int));
                t[0] = nums[i]; t[1] = nums[lo]; t[2] = nums[hi];
                res[count] = t;
                (*returnColumnSizes)[count++] = 3;
                lo++; hi--;
                while (lo < hi && nums[lo] == nums[lo - 1]) lo++;
                while (lo < hi && nums[hi] == nums[hi + 1]) hi--;
            }
        }
    }
    *returnSize = count;
    return res;
}
```

### Rust
```rust
pub fn three_sum(mut nums: Vec<i32>) -> Vec<Vec<i32>> {
    nums.sort_unstable();
    let mut res = Vec::new();
    let n = nums.len();
    if n < 3 { return res; }
    for i in 0..n - 2 {
        if nums[i] > 0 { break; }
        if i > 0 && nums[i] == nums[i - 1] { continue; }
        let (mut lo, mut hi) = (i + 1, n - 1);
        while lo < hi {
            let s = nums[i] + nums[lo] + nums[hi];
            if s < 0 { lo += 1; }
            else if s > 0 { hi -= 1; }
            else {
                res.push(vec![nums[i], nums[lo], nums[hi]]);
                lo += 1; hi -= 1;
                while lo < hi && nums[lo] == nums[lo - 1] { lo += 1; }
                while lo < hi && nums[hi] == nums[hi + 1] { hi -= 1; }
            }
        }
    }
    res
}
```
