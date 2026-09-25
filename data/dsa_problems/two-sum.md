---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: arrays, hash-map
fn_python: two_sum
fn_javascript: twoSum
test_cases: [{"args": [[2, 7, 11, 15], 9], "expected": [0, 1]}, {"args": [[3, 2, 4], 6], "expected": [1, 2]}, {"args": [[3, 3], 6], "expected": [0, 1]}, {"args": [[-1, -2, -3, -4], -6], "expected": [1, 3]}, {"args": [[0, 4, 3, 0], 0], "expected": [0, 3]}, {"args": [[1, 2], 3], "expected": [0, 1]}]
---
# Two Sum (LC 1) — Easy — Array, Hash Map

## Problem
Given an integer array `nums` and an integer `target`, return the indices of the two distinct elements that sum to `target`. Exactly one answer exists.

## Example
nums = [2,7,11,15], target = 9 → [0,1]

## Approach
Scan once, storing each value's index in a hash map. For each element x, check whether `target - x` was already seen. Time O(n), space O(n).

## Hints
- Brute force is O(n^2); trade space for time.
- Check the map for the complement BEFORE inserting x to avoid reusing the same element.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode. List/tree node definitions follow LeetCode's.*

### Python
```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []
```

### JavaScript
```javascript
function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    if (seen.has(target - nums[i])) return [seen.get(target - nums[i]), i];
    seen.set(nums[i], i);
  }
  return [];
}
```

### Java
```java
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        if (seen.containsKey(target - nums[i]))
            return new int[]{seen.get(target - nums[i]), i};
        seen.put(nums[i], i);
    }
    return new int[0];
}
```

### C++
```cpp
vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < (int)nums.size(); i++) {
        auto it = seen.find(target - nums[i]);
        if (it != seen.end()) return {it->second, i};
        seen[nums[i]] = i;
    }
    return {};
}
```

### C
```c
/* Simple open-addressing hash table; LeetCode's C signature. */
int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    int cap = numsSize * 2 + 1;
    int* keys = malloc(cap * sizeof(int));
    int* vals = malloc(cap * sizeof(int));
    char* used = calloc(cap, 1);
    int* res = malloc(2 * sizeof(int));
    *returnSize = 0;
    for (int i = 0; i < numsSize; i++) {
        long want = (long)target - nums[i];
        unsigned h = (unsigned)(want % cap + cap) % cap;
        while (used[h]) {
            if (keys[h] == want) {
                res[0] = vals[h]; res[1] = i; *returnSize = 2;
                free(keys); free(vals); free(used);
                return res;
            }
            h = (h + 1) % cap;
        }
        unsigned h2 = (unsigned)((long)nums[i] % cap + cap) % cap;
        while (used[h2]) h2 = (h2 + 1) % cap;
        used[h2] = 1; keys[h2] = nums[i]; vals[h2] = i;
    }
    free(keys); free(vals); free(used);
    return res;
}
```

### Rust
```rust
use std::collections::HashMap;
pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
    let mut seen = HashMap::new();
    for (i, &x) in nums.iter().enumerate() {
        if let Some(&j) = seen.get(&(target - x)) {
            return vec![j, i as i32];
        }
        seen.insert(x, i as i32);
    }
    vec![]
}
```
