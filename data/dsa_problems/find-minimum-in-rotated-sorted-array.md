---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: binary-search
fn_python: find_min
fn_javascript: findMin
fn_typescript: findMin
fn_java: findMin
fn_cpp: findMin
fn_c: findMin
fn_rust: find_min
fn_go: findMin
fn_csharp: FindMin
fn_ruby: find_min
test_cases: [{"args": [[7]], "expected": 7}, {"args": [[9, 8]], "expected": 8}, {"args": [[6, 7, 1, 2, 3, 4, 5]], "expected": 1}, {"args": [[20, 25, 30, 2, 5, 10, 15]], "expected": 2}, {"args": [[-3, 0, 4, -9, -5]], "expected": -9}, {"args": [[1000000000, -1000000000, 5]], "expected": -1000000000}, {"args": [[12, 13, 14, 15, 16, 17, 18, 19, 4]], "expected": 4}, {"args": [[8, 9]], "expected": 8}]
---
# Smallest Value After a Cyclic Shift — Medium — Binary Search

## Problem
You are given a list `nums` of distinct integers with at least one element. The list was produced in two steps: start from a strictly increasing sequence, then move some suffix of it to the front. The shift may be empty, in which case the list is still sorted.

Return the smallest value in the list. The solution must run in O(log n) time.

## Example
nums = [4, 6, 9, 0, 2, 3] → 0

## Approach
Binary search for the position of the smallest value. Compare the middle element with the last element. If the middle is larger than the last, the break point where the increasing run restarts lies strictly to the right of the middle, so the answer is there. Otherwise the smallest value sits at the middle or to its left. Shrink the window until only one index remains. Time O(log n), space O(1).

## Hints
- Compare against the right end, not the left: the left end may belong to either half of the shifted list.
- Keep the search window as a closed range `[lo, hi]` and stop when `lo == hi`.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[hi] < nums[mid]:
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
    const mid = lo + ((hi - lo) >> 1);
    if (nums[hi] < nums[mid]) lo = mid + 1;
    else hi = mid;
  }
  return nums[lo];
}
```

### TypeScript
```typescript
function findMin(nums: number[]): number {
  let lo = 0, hi = nums.length - 1;
  while (lo < hi) {
    const mid = lo + ((hi - lo) >> 1);
    if (nums[hi] < nums[mid]) lo = mid + 1;
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
        if (nums[hi] < nums[mid]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### C++
```cpp
int findMin(std::vector<int>& nums) {
    int lo = 0, hi = (int)nums.size() - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[hi] < nums[mid]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### C
```c
long long findMin(long long* nums, int numsSize) {
    int lo = 0, hi = numsSize - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[hi] < nums[mid]) lo = mid + 1;
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
        let mid = lo + (hi - lo) / 2;
        if nums[hi] < nums[mid] {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    nums[lo]
}
```

### Go
```go
func findMin(nums []int) int {
	lo, hi := 0, len(nums)-1
	for lo < hi {
		mid := lo + (hi-lo)/2
		if nums[hi] < nums[mid] {
			lo = mid + 1
		} else {
			hi = mid
		}
	}
	return nums[lo]
}
```

### C#
```csharp
public static int FindMin(int[] nums) {
    int lo = 0, hi = nums.Length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[hi] < nums[mid]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}
```

### Ruby
```ruby
def find_min(nums)
  lo, hi = 0, nums.length - 1
  while lo < hi
    mid = lo + (hi - lo) / 2
    if nums[hi] < nums[mid]
      lo = mid + 1
    else
      hi = mid
    end
  end
  nums[lo]
end
```
