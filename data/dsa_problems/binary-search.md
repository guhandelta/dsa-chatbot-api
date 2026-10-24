---
track: dsa
difficulty: Easy
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
test_cases: [{"args": [[], 5], "expected": -1}, {"args": [[7], 7], "expected": 0}, {"args": [[7], 8], "expected": -1}, {"args": [[1, 3, 5, 7, 9, 11], 1], "expected": 0}, {"args": [[1, 3, 5, 7, 9, 11], 11], "expected": 5}, {"args": [[1, 3, 5, 7, 9, 11], 4], "expected": -1}, {"args": [[-20, -7, 0, 3, 18, 42, 100], -7], "expected": 1}, {"args": [[-2000000000, -1, 0, 2000000000], 2000000000], "expected": 3}]
---
# Locate a Value in Sorted Data — Easy — Binary Search

## Problem
You are given a list `vals` of distinct integers sorted in strictly increasing order, and an integer `key`. Return the index at which `key` occurs in `vals`, or -1 if `key` does not occur. The solution must run in O(log n) time. Every value fits in a signed 32-bit integer.

## Example
vals = [2,4,6,8,10,12,14], key = 10 → 4

## Approach
Keep a window of candidate indices, from `lo` to `hi`. Look at the middle entry of the window and compare it with `key`. Because the list is sorted, one comparison discards the half of the window that cannot contain `key`. Repeat until the key is found or the window is empty. Time O(log n), space O(1).

## Hints
- Compute the middle as `lo + (hi - lo) / 2` so the sum never overflows a fixed-width integer.
- Keep looping while `lo <= hi` so that the last remaining candidate is still checked.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def search(vals, key):
    lo, hi = 0, len(vals) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if vals[mid] == key:
            return mid
        if vals[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### JavaScript
```javascript
function search(vals, key) {
  let lo = 0, hi = vals.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (vals[mid] === key) return mid;
    if (vals[mid] < key) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}
```

### TypeScript
```typescript
function search(vals: number[], key: number): number {
  let lo = 0, hi = vals.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (vals[mid] === key) return mid;
    if (vals[mid] < key) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}
```

### Java
```java
public int search(int[] vals, int key) {
    int lo = 0, hi = vals.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (vals[mid] == key) return mid;
        if (vals[mid] < key) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### C++
```cpp
#include <vector>
int search(std::vector<int>& vals, int key) {
    int lo = 0, hi = (int)vals.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (vals[mid] == key) return mid;
        if (vals[mid] < key) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### C
```c
long long search(long long* vals, int valsSize, long long key) {
    int lo = 0, hi = valsSize - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (vals[mid] == key) return mid;
        if (vals[mid] < key) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### Rust
```rust
pub fn search(vals: Vec<i32>, key: i32) -> i32 {
    let (mut lo, mut hi) = (0i32, vals.len() as i32 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        let v = vals[mid as usize];
        if v == key { return mid; }
        if v < key { lo = mid + 1; } else { hi = mid - 1; }
    }
    -1
}
```

### Go
```go
func search(vals []int, key int) int {
	lo, hi := 0, len(vals)-1
	for lo <= hi {
		mid := lo + (hi-lo)/2
		if vals[mid] == key {
			return mid
		}
		if vals[mid] < key {
			lo = mid + 1
		} else {
			hi = mid - 1
		}
	}
	return -1
}
```

### C#
```csharp
public static int Search(int[] vals, int key)
{
    int lo = 0, hi = vals.Length - 1;
    while (lo <= hi)
    {
        int mid = lo + (hi - lo) / 2;
        if (vals[mid] == key) return mid;
        if (vals[mid] < key) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### Ruby
```ruby
def search(vals, key)
  lo = 0
  hi = vals.length - 1
  while lo <= hi
    mid = lo + (hi - lo) / 2
    return mid if vals[mid] == key
    if vals[mid] < key
      lo = mid + 1
    else
      hi = mid - 1
    end
  end
  -1
end
```
