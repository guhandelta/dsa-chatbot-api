---
track: dsa
difficulty: Medium
source: authored
io_mode: function
comparison: unordered_nested
algorithms: arrays, sorting, two-pointers
fn_python: three_sum
fn_javascript: threeSum
fn_typescript: threeSum
fn_java: threeSum
fn_cpp: three_sum
fn_c: three_sum
fn_rust: three_sum
fn_go: threeSum
fn_csharp: ThreeSum
fn_ruby: three_sum
test_cases: [{"args": [[1, 2, 3]], "expected": []}, {"args": [[]], "expected": []}, {"args": [[0, 0, 0, 0, 0]], "expected": [[0, 0, 0]]}, {"args": [[5, -5, 0]], "expected": [[-5, 0, 5]]}, {"args": [[-4, -4, -4, 8, 4]], "expected": [[-4, -4, 8]]}, {"args": [[3, -1, -2, 1, 1, -1, 2]], "expected": [[-2, -1, 3], [-2, 1, 1], [-1, -1, 2]]}, {"args": [[-1000000000, 1000000000, 0, 7]], "expected": [[-1000000000, 0, 1000000000]]}, {"args": [[6, -6, 6, -6, 0]], "expected": [[-6, 0, 6]]}]
---
# Triplets That Net to Zero — Medium — Array, Two Pointers, Sorting

## Problem
You are given a list of integers `values`. Return every distinct triple of entries whose sum is exactly zero. The three entries of a triple must come from three different positions in the list, but two triples count as the same when they contain the same three values, so no triple may appear twice in the result. Write each triple as a list of three integers in non-decreasing order. The order of the triples in the result does not matter. If no triple exists, return an empty list.

## Example
values = [4,-1,-3,2,-2,0] → [[-3,-1,4],[-2,0,2]]

## Approach
Sort the list. Fix one entry at position i, then search the entries to its right with two pointers, one starting at each end, for a pair whose sum equals the negation of the fixed value. Moving the pointers depends on whether the running total is too small or too large. Skip repeated values at each choice of i and again after every match, so no triple is reported twice. Time O(n^2), extra space O(1) beyond the output.

## Hints
- Once the list is sorted, the two-pointer scan can decide which pointer to move from the sign of the running total.
- After recording a match, move both pointers past any equal neighbours so the same triple is not produced again.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def three_sum(values):
    values.sort()
    out = []
    n = len(values)
    for i in range(n - 2):
        if values[i] > 0:
            break
        if i > 0 and values[i] == values[i - 1]:
            continue
        lo, hi = i + 1, n - 1
        while lo < hi:
            total = values[i] + values[lo] + values[hi]
            if total < 0:
                lo += 1
            elif total > 0:
                hi -= 1
            else:
                out.append([values[i], values[lo], values[hi]])
                lo += 1
                hi -= 1
                while lo < hi and values[lo] == values[lo - 1]:
                    lo += 1
                while lo < hi and values[hi] == values[hi + 1]:
                    hi -= 1
    return out
```

### JavaScript
```javascript
function threeSum(values) {
  values.sort((a, b) => a - b);
  const out = [];
  const n = values.length;
  for (let i = 0; i < n - 2; i++) {
    if (values[i] > 0) break;
    if (i > 0 && values[i] === values[i - 1]) continue;
    let lo = i + 1, hi = n - 1;
    while (lo < hi) {
      const total = values[i] + values[lo] + values[hi];
      if (total < 0) lo++;
      else if (total > 0) hi--;
      else {
        out.push([values[i], values[lo], values[hi]]);
        lo++; hi--;
        while (lo < hi && values[lo] === values[lo - 1]) lo++;
        while (lo < hi && values[hi] === values[hi + 1]) hi--;
      }
    }
  }
  return out;
}
```

### TypeScript
```typescript
function threeSum(values: number[]): number[][] {
  values.sort((a, b) => a - b);
  const out: number[][] = [];
  const n = values.length;
  for (let i = 0; i < n - 2; i++) {
    if (values[i] > 0) break;
    if (i > 0 && values[i] === values[i - 1]) continue;
    let lo = i + 1, hi = n - 1;
    while (lo < hi) {
      const total = values[i] + values[lo] + values[hi];
      if (total < 0) lo++;
      else if (total > 0) hi--;
      else {
        out.push([values[i], values[lo], values[hi]]);
        lo++; hi--;
        while (lo < hi && values[lo] === values[lo - 1]) lo++;
        while (lo < hi && values[hi] === values[hi + 1]) hi--;
      }
    }
  }
  return out;
}
```

### Java
```java
public List<List<Integer>> threeSum(int[] values) {
    Arrays.sort(values);
    List<List<Integer>> out = new ArrayList<>();
    int n = values.length;
    for (int i = 0; i < n - 2; i++) {
        if (values[i] > 0) break;
        if (i > 0 && values[i] == values[i - 1]) continue;
        int lo = i + 1, hi = n - 1;
        while (lo < hi) {
            int total = values[i] + values[lo] + values[hi];
            if (total < 0) lo++;
            else if (total > 0) hi--;
            else {
                out.add(Arrays.asList(values[i], values[lo], values[hi]));
                lo++; hi--;
                while (lo < hi && values[lo] == values[lo - 1]) lo++;
                while (lo < hi && values[hi] == values[hi + 1]) hi--;
            }
        }
    }
    return out;
}
```

### C++
```cpp
#include <algorithm>
#include <vector>
std::vector<std::vector<int>> three_sum(std::vector<int>& values) {
    std::sort(values.begin(), values.end());
    std::vector<std::vector<int>> out;
    int n = values.size();
    for (int i = 0; i < n - 2; i++) {
        if (values[i] > 0) break;
        if (i > 0 && values[i] == values[i - 1]) continue;
        int lo = i + 1, hi = n - 1;
        while (lo < hi) {
            int total = values[i] + values[lo] + values[hi];
            if (total < 0) lo++;
            else if (total > 0) hi--;
            else {
                out.push_back({values[i], values[lo], values[hi]});
                lo++; hi--;
                while (lo < hi && values[lo] == values[lo - 1]) lo++;
                while (lo < hi && values[hi] == values[hi + 1]) hi--;
            }
        }
    }
    return out;
}
```

### C
```c
static int cmp_int(const void* a, const void* b) {
    int x = *(const int*)a, y = *(const int*)b;
    return (x > y) - (x < y);
}
/* Returns an array of triples; each triple is a malloc'd array of 3 ints. */
int** three_sum(int* values, int valuesSize, int* returnSize, int** returnColumnSizes) {
    qsort(values, valuesSize, sizeof(int), cmp_int);
    int cap = 64, count = 0;
    int** out = malloc(cap * sizeof(int*));
    *returnColumnSizes = malloc(cap * sizeof(int));
    for (int i = 0; i < valuesSize - 2; i++) {
        if (values[i] > 0) break;
        if (i > 0 && values[i] == values[i - 1]) continue;
        int lo = i + 1, hi = valuesSize - 1;
        while (lo < hi) {
            int total = values[i] + values[lo] + values[hi];
            if (total < 0) lo++;
            else if (total > 0) hi--;
            else {
                if (count == cap) {
                    cap *= 2;
                    out = realloc(out, cap * sizeof(int*));
                    *returnColumnSizes = realloc(*returnColumnSizes, cap * sizeof(int));
                }
                int* t = malloc(3 * sizeof(int));
                t[0] = values[i]; t[1] = values[lo]; t[2] = values[hi];
                out[count] = t;
                (*returnColumnSizes)[count++] = 3;
                lo++; hi--;
                while (lo < hi && values[lo] == values[lo - 1]) lo++;
                while (lo < hi && values[hi] == values[hi + 1]) hi--;
            }
        }
    }
    *returnSize = count;
    return out;
}
```

### Rust
```rust
pub fn three_sum(mut values: Vec<i32>) -> Vec<Vec<i32>> {
    values.sort_unstable();
    let mut out = Vec::new();
    let n = values.len();
    if n < 3 { return out; }
    for i in 0..n - 2 {
        if values[i] > 0 { break; }
        if i > 0 && values[i] == values[i - 1] { continue; }
        let (mut lo, mut hi) = (i + 1, n - 1);
        while lo < hi {
            let total = values[i] + values[lo] + values[hi];
            if total < 0 { lo += 1; }
            else if total > 0 { hi -= 1; }
            else {
                out.push(vec![values[i], values[lo], values[hi]]);
                lo += 1; hi -= 1;
                while lo < hi && values[lo] == values[lo - 1] { lo += 1; }
                while lo < hi && values[hi] == values[hi + 1] { hi -= 1; }
            }
        }
    }
    out
}
```

### Go
```go
import "sort"

func threeSum(values []int) [][]int {
	sort.Ints(values)
	out := [][]int{}
	n := len(values)
	for i := 0; i < n-2; i++ {
		if values[i] > 0 {
			break
		}
		if i > 0 && values[i] == values[i-1] {
			continue
		}
		lo, hi := i+1, n-1
		for lo < hi {
			total := values[i] + values[lo] + values[hi]
			if total < 0 {
				lo++
			} else if total > 0 {
				hi--
			} else {
				out = append(out, []int{values[i], values[lo], values[hi]})
				lo++
				hi--
				for lo < hi && values[lo] == values[lo-1] {
					lo++
				}
				for lo < hi && values[hi] == values[hi+1] {
					hi--
				}
			}
		}
	}
	return out
}
```

### C#
```csharp
public static System.Collections.Generic.IList<System.Collections.Generic.IList<int>> ThreeSum(int[] values)
{
    System.Array.Sort(values);
    var out_ = new System.Collections.Generic.List<System.Collections.Generic.IList<int>>();
    int n = values.Length;
    for (int i = 0; i < n - 2; i++)
    {
        if (values[i] > 0) break;
        if (i > 0 && values[i] == values[i - 1]) continue;
        int lo = i + 1, hi = n - 1;
        while (lo < hi)
        {
            int total = values[i] + values[lo] + values[hi];
            if (total < 0) lo++;
            else if (total > 0) hi--;
            else
            {
                out_.Add(new System.Collections.Generic.List<int> { values[i], values[lo], values[hi] });
                lo++; hi--;
                while (lo < hi && values[lo] == values[lo - 1]) lo++;
                while (lo < hi && values[hi] == values[hi + 1]) hi--;
            }
        }
    }
    return out_;
}
```

### Ruby
```ruby
def three_sum(values)
  values = values.sort
  out = []
  n = values.length
  (0...(n - 2)).each do |i|
    break if values[i] > 0
    next if i > 0 && values[i] == values[i - 1]
    lo = i + 1
    hi = n - 1
    while lo < hi
      total = values[i] + values[lo] + values[hi]
      if total < 0
        lo += 1
      elsif total > 0
        hi -= 1
      else
        out << [values[i], values[lo], values[hi]]
        lo += 1
        hi -= 1
        lo += 1 while lo < hi && values[lo] == values[lo - 1]
        hi -= 1 while lo < hi && values[hi] == values[hi + 1]
      end
    end
  end
  out
end
```
