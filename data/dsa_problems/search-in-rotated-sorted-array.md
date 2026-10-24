---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: binary-search
fn_python: search
fn_javascript: search
fn_typescript: search
fn_java: search
fn_cpp: search
fn_c: search
fn_rust: search
fn_go: search
fn_csharp: Search
fn_ruby: search
test_cases: [{"args": [[9, 11, 13, 2, 5, 7], 2], "expected": 3}, {"args": [[9, 11, 13, 2, 5, 7], 6], "expected": -1}, {"args": [[8], 8], "expected": 0}, {"args": [[8], 3], "expected": -1}, {"args": [[2, 4], 4], "expected": 1}, {"args": [[3, 4, 6, 1], 1], "expected": 3}, {"args": [[3, 4, 6, 1], 5], "expected": -1}, {"args": [[12, 40, -7, -3, 0, 5], -7], "expected": 2}, {"args": [[0, 2147483647, -2147483648], -2147483648], "expected": 2}, {"args": [[5, 7, 1, 3], 7], "expected": 1}]
algorithms: binary-search
---
# Locate a Value in a Shifted Sorted List — Medium — Binary Search

## Problem
Start with a strictly increasing list of distinct integers. Then move some prefix of that list (possibly an empty one) to the end, keeping the order inside the prefix. The result is the array `nums` you receive. Its values are all distinct, and reading it cyclically it goes up in one continuous run.

Given `nums` and an integer `target`, return the index in `nums` where `target` sits, or -1 if `target` is not present. Indices refer to the array you were given, not to the position the value would have in the original sorted list. Every value is a 32-bit signed integer and `nums` has at least one element. Your solution must run in O(log n) time.

## Example
nums = [12, 40, -7, -3, 0, 5], target = -3 → 3

## Approach
Binary search, with one extra question per probe. Keep a window [lo, hi] and look at the middle index `mid`. Because the list was shifted only once, at least one of the two halves [lo, mid] or [mid, hi] is still in increasing order. Check whether `nums[lo] <= nums[mid]`: if so, the left half is the ordered one, and you test whether `target` lies within that half's range; if it does, keep the left half, otherwise keep the right half. If the right half is the ordered one, do the mirrored test. Stop when `mid` holds the target or the window becomes empty. Time O(log n), space O(1).

## Hints
- Compare `nums[lo]` with `nums[mid]` to learn which side is in order.
- Once you know which side is ordered, a range check against its two ends decides where the target can be.

## Solutions
*Conventions: Java code sits in `class Solution`. C++ uses `std::vector` with its header included. Rust takes an owned `Vec<i32>`. C takes a pointer to 64-bit values plus a length.*

### Python
```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
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
    const mid = Math.floor((lo + hi) / 2);
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

### TypeScript
```typescript
function search(nums: number[], target: number): number {
  let lo = 0, hi = nums.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
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
class Solution {
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
}
```

### C++
```cpp
#include <vector>

int search(std::vector<int>& nums, int target) {
    int lo = 0, hi = (int)nums.size() - 1;
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
int search(long long* nums, int numsSize, long long target) {
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
    let (mut lo, mut hi) = (0i64, nums.len() as i64 - 1);
    while lo <= hi {
        let mid = (lo + hi) / 2;
        let (l, m, h) = (nums[lo as usize], nums[mid as usize], nums[hi as usize]);
        if m == target {
            return mid as i32;
        }
        if l <= m {
            if l <= target && target < m { hi = mid - 1; } else { lo = mid + 1; }
        } else {
            if m < target && target <= h { lo = mid + 1; } else { hi = mid - 1; }
        }
    }
    -1
}
```

### Go
```go
func search(nums []int, target int) int {
	lo, hi := 0, len(nums)-1
	for lo <= hi {
		mid := lo + (hi-lo)/2
		if nums[mid] == target {
			return mid
		}
		if nums[lo] <= nums[mid] {
			if nums[lo] <= target && target < nums[mid] {
				hi = mid - 1
			} else {
				lo = mid + 1
			}
		} else {
			if nums[mid] < target && target <= nums[hi] {
				lo = mid + 1
			} else {
				hi = mid - 1
			}
		}
	}
	return -1
}
```

### C#
```csharp
public static class Solution {
    public static int Search(int[] nums, int target) {
        int lo = 0, hi = nums.Length - 1;
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
}
```

### Ruby
```ruby
def search(nums, target)
  lo = 0
  hi = nums.length - 1
  while lo <= hi
    mid = (lo + hi) / 2
    return mid if nums[mid] == target
    if nums[lo] <= nums[mid]
      if nums[lo] <= target && target < nums[mid]
        hi = mid - 1
      else
        lo = mid + 1
      end
    else
      if nums[mid] < target && target <= nums[hi]
        lo = mid + 1
      else
        hi = mid - 1
      end
    end
  end
  -1
end
```
