---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: two-pointers
fn_python: max_area
fn_javascript: maxArea
fn_typescript: maxArea
fn_java: maxArea
fn_cpp: maxArea
fn_c: maxArea
fn_rust: max_area
fn_go: maxArea
fn_csharp: MaxArea
fn_ruby: max_area
test_cases: [{"args": [[5, 0]], "expected": 0}, {"args": [[3, 3, 3, 3]], "expected": 9}, {"args": [[1, 2, 4, 3]], "expected": 4}, {"args": [[6, 1, 4, 7, 2, 5]], "expected": 25}, {"args": [[9, 0, 0, 0, 0, 9]], "expected": 45}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], "expected": 25}, {"args": [[1000000000, 1, 1000000000]], "expected": 2000000000}, {"args": [[2, 9]], "expected": 2}]
---
# Most Water Between Two Walls — Medium — Two Pointers

## Problem
You are given a list `heights` of at least two non-negative integers. Entry `heights[i]` is the height of a vertical wall standing at position `i`.

Choose two different walls at positions `i < j`. The water they hold is a rectangle whose width is `j - i` and whose height is the shorter of the two walls, so its area is `(j - i) × min(heights[i], heights[j])`. Return the largest area that any choice of two walls can hold.

## Example
heights = [4, 1, 3, 2, 5] → 16 (walls at positions 0 and 4: width 4, shorter wall 4)

## Approach
Start with one index at each end of the list. The area is limited by the shorter wall, so moving the taller index inward can never beat the current pair: the width shrinks and the height cannot grow past the shorter wall. Always move the index that points at the shorter wall, and record the best area seen at each step. Time O(n), space O(1).

## Hints
- When the two ends have different heights, which wall is safe to discard?
- Keep a running maximum while the two indices move toward each other.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def max_area(height):
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        span = right - left
        best = max(best, span * min(height[left], height[right]))
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1
    return best
```

### JavaScript
```javascript
function maxArea(height) {
  let l = 0, r = height.length - 1, best = 0;
  while (l < r) {
    best = Math.max(best, (r - l) * Math.min(height[l], height[r]));
    if (height[l] <= height[r]) l++;
    else r--;
  }
  return best;
}
```

### TypeScript
```typescript
function maxArea(height: number[]): number {
  let l = 0, r = height.length - 1, best = 0;
  while (l < r) {
    best = Math.max(best, (r - l) * Math.min(height[l], height[r]));
    if (height[l] <= height[r]) l++;
    else r--;
  }
  return best;
}
```

### Java
```java
public int maxArea(int[] height) {
    int l = 0, r = height.length - 1, best = 0;
    while (l < r) {
        best = Math.max(best, (r - l) * Math.min(height[l], height[r]));
        if (height[l] <= height[r]) l++;
        else r--;
    }
    return best;
}
```

### C++
```cpp
int maxArea(std::vector<int>& height) {
    int l = 0, r = (int)height.size() - 1, best = 0;
    while (l < r) {
        best = std::max(best, (r - l) * std::min(height[l], height[r]));
        if (height[l] <= height[r]) l++;
        else r--;
    }
    return best;
}
```

### C
```c
long long maxArea(long long* height, int heightSize) {
    int l = 0, r = heightSize - 1;
    long long best = 0;
    while (l < r) {
        long long low = height[l] < height[r] ? height[l] : height[r];
        long long area = (long long)(r - l) * low;
        if (area > best) best = area;
        if (height[l] <= height[r]) l++;
        else r--;
    }
    return best;
}
```

### Rust
```rust
pub fn max_area(height: Vec<i32>) -> i32 {
    let (mut l, mut r) = (0usize, height.len() - 1);
    let mut best = 0i32;
    while l < r {
        let area = (r - l) as i32 * height[l].min(height[r]);
        best = best.max(area);
        if height[l] <= height[r] {
            l += 1;
        } else {
            r -= 1;
        }
    }
    best
}
```

### Go
```go
func maxArea(height []int) int {
	l, r, best := 0, len(height)-1, 0
	for l < r {
		low := height[l]
		if height[r] < low {
			low = height[r]
		}
		if area := (r - l) * low; area > best {
			best = area
		}
		if height[l] <= height[r] {
			l++
		} else {
			r--
		}
	}
	return best
}
```

### C#
```csharp
public static int MaxArea(int[] height) {
    int l = 0, r = height.Length - 1, best = 0;
    while (l < r) {
        int area = (r - l) * Math.Min(height[l], height[r]);
        best = Math.Max(best, area);
        if (height[l] <= height[r]) l++;
        else r--;
    }
    return best;
}
```

### Ruby
```ruby
def max_area(height)
  l, r, best = 0, height.length - 1, 0
  while l < r
    area = (r - l) * [height[l], height[r]].min
    best = area if area > best
    if height[l] <= height[r]
      l += 1
    else
      r -= 1
    end
  end
  best
end
```
