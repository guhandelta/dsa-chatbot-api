---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: dynamic-programming
fn_python: combination_sum4
fn_javascript: combinationSum4
fn_typescript: combinationSum4
fn_java: combinationSum4
fn_cpp: combinationSum4
fn_c: combinationSum4
fn_rust: combination_sum4
fn_go: combinationSum4
fn_csharp: CombinationSum4
fn_ruby: combination_sum4
test_cases: [{"args": [[1, 2], 4], "expected": 5}, {"args": [[2, 4, 6], 0], "expected": 1}, {"args": [[5], 12], "expected": 0}, {"args": [[1], 7], "expected": 1}, {"args": [[2, 3], 5], "expected": 2}, {"args": [[1, 2, 3], 6], "expected": 24}, {"args": [[3, 1, 4, 2], 10], "expected": 401}, {"args": [[7, 2, 5], 20], "expected": 63}, {"args": [[1, 3], 20], "expected": 1278}, {"args": [[10, 20, 30], 90], "expected": 149}]
---
# Counting Ordered Step Sequences — Medium — DP

## Problem
You are given a list `steps` of distinct positive integers and a non-negative integer `goal`. Count the sequences whose entries are all taken from `steps`, may reuse any step value as often as needed, and add up to `goal`. Order matters: two sequences that hold the same values in a different order are counted as different sequences.

When `goal` is 0, the empty sequence is the only one, so the answer is 1. Return the count. The answer always fits in a 32-bit signed integer for the inputs used here.

## Example
steps = [1, 3], goal = 5 → 4 (1+1+1+1+1, 1+1+3, 1+3+1, 3+1+1)

## Approach
Let `ways[s]` be the number of ordered sequences whose sum is `s`. Set `ways[0] = 1`. For every other `s`, the last step taken can be any value `x` in `steps` with `x <= s`, and the sequences before it sum to `s - x`, so `ways[s]` is the sum of `ways[s - x]` over those choices. Fill `s` from 0 up to `goal`. Time O(goal × number of steps), space O(goal).

## Hints
- Summing over every possible last step is what makes the order count.
- Swapping the two loops (steps outermost, totals innermost) counts unordered groups instead, which is a different question.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def combination_sum4(nums, target):
    ways = [1] + [0] * target
    for s in range(1, target + 1):
        ways[s] = sum(ways[s - x] for x in nums if x <= s)
    return ways[target]
```

### JavaScript
```javascript
function combinationSum4(nums, target) {
  const ways = new Array(target + 1).fill(0);
  ways[0] = 1;
  for (let s = 1; s <= target; s++)
    for (const x of nums)
      if (x <= s) ways[s] += ways[s - x];
  return ways[target];
}
```

### TypeScript
```typescript
function combinationSum4(nums: number[], target: number): number {
  const ways: number[] = new Array(target + 1).fill(0);
  ways[0] = 1;
  for (let s = 1; s <= target; s++)
    for (const x of nums)
      if (x <= s) ways[s] += ways[s - x];
  return ways[target];
}
```

### Java
```java
public int combinationSum4(int[] nums, int target) {
    int[] ways = new int[target + 1];
    ways[0] = 1;
    for (int s = 1; s <= target; s++)
        for (int x : nums)
            if (x <= s) ways[s] += ways[s - x];
    return ways[target];
}
```

### C++
```cpp
int combinationSum4(std::vector<int>& nums, int target) {
    std::vector<long long> ways(target + 1, 0);
    ways[0] = 1;
    for (int s = 1; s <= target; s++)
        for (int x : nums)
            if (x <= s) ways[s] += ways[s - x];
    return (int)ways[target];
}
```

### C
```c
long long combinationSum4(long long* nums, int numsSize, long long target) {
    long long* ways = calloc(target + 1, sizeof(long long));
    ways[0] = 1;
    for (long long s = 1; s <= target; s++)
        for (int i = 0; i < numsSize; i++)
            if (nums[i] <= s) ways[s] += ways[s - nums[i]];
    long long result = ways[target];
    free(ways);
    return result;
}
```

### Rust
```rust
pub fn combination_sum4(nums: Vec<i32>, target: i32) -> i32 {
    let goal = target as usize;
    let mut ways = vec![0u64; goal + 1];
    ways[0] = 1;
    for s in 1..=goal {
        for &x in nums.iter() {
            let x = x as usize;
            if x <= s {
                ways[s] += ways[s - x];
            }
        }
    }
    ways[goal] as i32
}
```

### Go
```go
func combinationSum4(nums []int, target int) int {
	ways := make([]int, target+1)
	ways[0] = 1
	for s := 1; s <= target; s++ {
		for _, x := range nums {
			if x <= s {
				ways[s] += ways[s-x]
			}
		}
	}
	return ways[target]
}
```

### C#
```csharp
public static int CombinationSum4(int[] nums, int target) {
    int[] ways = new int[target + 1];
    ways[0] = 1;
    for (int s = 1; s <= target; s++)
        foreach (int x in nums)
            if (x <= s) ways[s] += ways[s - x];
    return ways[target];
}
```

### Ruby
```ruby
def combination_sum4(nums, target)
  ways = Array.new(target + 1, 0)
  ways[0] = 1
  (1..target).each do |s|
    nums.each { |x| ways[s] += ways[s - x] if x <= s }
  end
  ways[target]
end
```
