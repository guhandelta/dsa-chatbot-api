---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: two-pointers
fn_python: max_area
fn_javascript: maxArea
test_cases: [{"args": [[1, 8, 6, 2, 5, 4, 8, 3, 7]], "expected": 49}, {"args": [[1, 1]], "expected": 1}, {"args": [[4, 3, 2, 1, 4]], "expected": 16}, {"args": [[1, 2, 1]], "expected": 2}, {"args": [[2, 3, 4, 5, 18, 17, 6]], "expected": 17}, {"args": [[1, 2]], "expected": 1}]
---
# Container With Most Water (LC 11) — Medium — Two Pointers

## Problem
Given heights of n vertical lines, pick two that, with the x-axis, contain the most water. Return the maximum area: width × min(height of the two).

## Example
[1,8,6,2,5,4,8,3,7] → 49

## Approach
Two pointers at the ends; the area is limited by the shorter line, so moving the taller pointer inward can never help — always move the shorter one. Time O(n), space O(1).

## Hints
- Why is it safe to discard the shorter line? Any pair using it with smaller width is worse.
- Track the best area as the pointers converge.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def max_area(height):
    lo, hi, best = 0, len(height) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(height[lo], height[hi]))
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best
```

### JavaScript
```javascript
function maxArea(height) {
  let lo = 0, hi = height.length - 1, best = 0;
  while (lo < hi) {
    best = Math.max(best, (hi - lo) * Math.min(height[lo], height[hi]));
    if (height[lo] < height[hi]) lo++;
    else hi--;
  }
  return best;
}
```

### Java
```java
public int maxArea(int[] height) {
    int lo = 0, hi = height.length - 1, best = 0;
    while (lo < hi) {
        best = Math.max(best, (hi - lo) * Math.min(height[lo], height[hi]));
        if (height[lo] < height[hi]) lo++;
        else hi--;
    }
    return best;
}
```

### C++
```cpp
int maxArea(vector<int>& height) {
    int lo = 0, hi = height.size() - 1, best = 0;
    while (lo < hi) {
        best = max(best, (hi - lo) * min(height[lo], height[hi]));
        if (height[lo] < height[hi]) lo++;
        else hi--;
    }
    return best;
}
```

### C
```c
int maxArea(int* height, int heightSize) {
    int lo = 0, hi = heightSize - 1, best = 0;
    while (lo < hi) {
        int h = height[lo] < height[hi] ? height[lo] : height[hi];
        int area = (hi - lo) * h;
        if (area > best) best = area;
        if (height[lo] < height[hi]) lo++;
        else hi--;
    }
    return best;
}
```

### Rust
```rust
pub fn max_area(height: Vec<i32>) -> i32 {
    let (mut lo, mut hi, mut best) = (0usize, height.len() - 1, 0i32);
    while lo < hi {
        let area = (hi - lo) as i32 * height[lo].min(height[hi]);
        best = best.max(area);
        if height[lo] < height[hi] { lo += 1; } else { hi -= 1; }
    }
    best
}
```
