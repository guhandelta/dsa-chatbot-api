---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: binary-search, dynamic-programming
fn_python: length_of_lis
fn_javascript: lengthOfLIS
fn_typescript: lengthOfLIS
fn_java: lengthOfLIS
fn_cpp: lengthOfLIS
fn_c: lengthOfLIS
fn_rust: length_of_lis
fn_go: lengthOfLIS
fn_csharp: LengthOfLIS
fn_ruby: length_of_lis
test_cases: [{"args": [[4]], "expected": 1}, {"args": [[2, 2, 2, 3, 3, 3]], "expected": 2}, {"args": [[6, 1, 8, 2, 9, 3, 10]], "expected": 4}, {"args": [[-1, 0, -2, 5, -3, 6, 7]], "expected": 5}, {"args": [[1000000000, -1000000000, 0, 1, 999999999]], "expected": 4}, {"args": [[0, 0, 0, 0, 0]], "expected": 1}, {"args": [[1, 2, 3, 4, 5, 6, 7, 8]], "expected": 8}, {"args": [[8, 6, 4, 2, 9, 1, 7, 3, 5]], "expected": 3}]
---
# Longest Strictly Rising Subsequence — Medium — DP, Binary Search

## Problem
You are given a non-empty list `values` of integers. Choose any set of positions and read the chosen values from left to right. The picks form a strictly rising run when each value is greater than the one before it.

Return the largest number of picks that can form a strictly rising run. The picked positions need not be adjacent, and two equal values can never both be picked.

## Example
values = [3, 10, 2, 1, 20] → 3 (for example 3, 10, 20)

## Approach
Keep a list `ends`, where `ends[k]` is the smallest possible last value of a strictly rising run of length `k + 1` found so far. The list stays sorted. For each new value, binary-search for the first entry that is not smaller than it. Overwrite that entry with the new value, or append the value if no such entry exists. The final length of `ends` is the answer. Time O(n log n), space O(n).

## Hints
- Replacing an entry with a smaller value never shortens any run already found, and it leaves room for longer runs later.
- Search for the first entry that is greater than or equal to the value, because equal values must not extend a run.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
import bisect

def length_of_lis(nums):
    ends = []
    for value in nums:
        pos = bisect.bisect_left(ends, value)
        if pos == len(ends):
            ends.append(value)
        else:
            ends[pos] = value
    return len(ends)
```

### JavaScript
```javascript
function lengthOfLIS(nums) {
  const ends = [];
  for (const value of nums) {
    let lo = 0, hi = ends.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (ends[mid] < value) lo = mid + 1;
      else hi = mid;
    }
    ends[lo] = value;
  }
  return ends.length;
}
```

### TypeScript
```typescript
function lengthOfLIS(nums: number[]): number {
  const ends: number[] = [];
  for (const value of nums) {
    let lo = 0, hi = ends.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (ends[mid] < value) lo = mid + 1;
      else hi = mid;
    }
    ends[lo] = value;
  }
  return ends.length;
}
```

### Java
```java
public int lengthOfLIS(int[] nums) {
    int[] ends = new int[nums.length];
    int len = 0;
    for (int value : nums) {
        int lo = 0, hi = len;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (ends[mid] < value) lo = mid + 1;
            else hi = mid;
        }
        ends[lo] = value;
        if (lo == len) len++;
    }
    return len;
}
```

### C++
```cpp
int lengthOfLIS(std::vector<int>& nums) {
    std::vector<int> ends;
    for (int value : nums) {
        auto pos = std::lower_bound(ends.begin(), ends.end(), value);
        if (pos == ends.end()) ends.push_back(value);
        else *pos = value;
    }
    return (int)ends.size();
}
```

### C
```c
long long lengthOfLIS(long long* nums, int numsSize) {
    long long* ends = malloc((numsSize > 0 ? numsSize : 1) * sizeof(long long));
    long long len = 0;
    for (int i = 0; i < numsSize; i++) {
        long long lo = 0, hi = len;
        while (lo < hi) {
            long long mid = lo + (hi - lo) / 2;
            if (ends[mid] < nums[i]) lo = mid + 1;
            else hi = mid;
        }
        ends[lo] = nums[i];
        if (lo == len) len++;
    }
    free(ends);
    return len;
}
```

### Rust
```rust
pub fn length_of_lis(nums: Vec<i32>) -> i32 {
    let mut ends: Vec<i32> = Vec::new();
    for value in nums {
        let pos = ends.partition_point(|&e| e < value);
        if pos == ends.len() {
            ends.push(value);
        } else {
            ends[pos] = value;
        }
    }
    ends.len() as i32
}
```

### Go
```go
func lengthOfLIS(nums []int) int {
	ends := []int{}
	for _, value := range nums {
		lo, hi := 0, len(ends)
		for lo < hi {
			mid := (lo + hi) / 2
			if ends[mid] < value {
				lo = mid + 1
			} else {
				hi = mid
			}
		}
		if lo == len(ends) {
			ends = append(ends, value)
		} else {
			ends[lo] = value
		}
	}
	return len(ends)
}
```

### C#
```csharp
public static int LengthOfLIS(int[] nums) {
    List<int> ends = new List<int>();
    foreach (int value in nums) {
        int lo = 0, hi = ends.Count;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (ends[mid] < value) lo = mid + 1;
            else hi = mid;
        }
        if (lo == ends.Count) ends.Add(value);
        else ends[lo] = value;
    }
    return ends.Count;
}
```

### Ruby
```ruby
def length_of_lis(nums)
  ends = []
  nums.each do |value|
    lo, hi = 0, ends.length
    while lo < hi
      mid = (lo + hi) / 2
      if ends[mid] < value
        lo = mid + 1
      else
        hi = mid
      end
    end
    if lo == ends.length
      ends << value
    else
      ends[lo] = value
    end
  end
  ends.length
end
```
