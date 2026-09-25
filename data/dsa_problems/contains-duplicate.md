---
track: dsa
difficulty: Easy
source: leetcode
io_mode: function
algorithms: arrays, hash-map
fn_python: contains_duplicate
fn_javascript: containsDuplicate
test_cases: [{"args": [[1, 2, 3, 1]], "expected": true}, {"args": [[1, 2, 3, 4]], "expected": false}, {"args": [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], "expected": true}, {"args": [[1]], "expected": false}, {"args": [[-1, -1]], "expected": true}, {"args": [[0, 1, 2]], "expected": false}]
---
# Contains Duplicate (LC 217) — Easy — Array, Hash Set

## Problem
Return true if any value appears at least twice in the integer array `nums`; false if every element is distinct.

## Example
[1,2,3,1] → true

## Approach
Insert into a hash set while scanning; a failed insert (value already present) means a duplicate. Time O(n), space O(n). (Sorting gives O(n log n)/O(1).)

## Hints
- A set answers "have I seen this?" in O(1).
- Compare set size to array length as a one-liner alternative.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def contains_duplicate(nums):
    return len(set(nums)) != len(nums)
```

### JavaScript
```javascript
function containsDuplicate(nums) {
  return new Set(nums).size !== nums.length;
}
```

### Java
```java
public boolean containsDuplicate(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) if (!seen.add(x)) return true;
    return false;
}
```

### C++
```cpp
bool containsDuplicate(vector<int>& nums) {
    unordered_set<int> seen;
    for (int x : nums) if (!seen.insert(x).second) return true;
    return false;
}
```

### C
```c
static int cmp_int(const void* a, const void* b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}
bool containsDuplicate(int* nums, int numsSize) {
    qsort(nums, numsSize, sizeof(int), cmp_int);   /* O(n log n), O(1) extra */
    for (int i = 1; i < numsSize; i++)
        if (nums[i] == nums[i - 1]) return true;
    return false;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn contains_duplicate(nums: Vec<i32>) -> bool {
    let mut seen = HashSet::new();
    nums.into_iter().any(|x| !seen.insert(x))
}
```
