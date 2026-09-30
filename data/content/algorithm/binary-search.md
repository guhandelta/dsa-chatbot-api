---
track: algorithm
difficulty: Medium
algorithms: binary-search
category: Algorithm
source: authored
io_mode: function
---
# Binary search — Medium — Algorithm

Binary search halves a sorted range each step. The safest template finds the lower bound: the first index in the half-open range \[lo, hi) where `a[i] >= target`, returning the array length when every element is smaller. It cannot loop forever because the range strictly shrinks. For the upper bound (first index with `a[i] > target`) change `<` to `<=`. In fixed-width languages compute the midpoint as `lo + (hi - lo) / 2` (or an unsigned shift) because `(lo + hi) / 2` overflows when both exceed half the integer range.

#### Binary search — Python

```python
def lower_bound(a, target):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

#### Binary search — JavaScript

```javascript
function lowerBound(a, target) {
  let lo = 0, hi = a.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (a[mid] < target) lo = mid + 1; else hi = mid;
  }
  return lo;
}
```

#### Binary search — TypeScript

```typescript
function lowerBound<T>(a: readonly T[], target: T, cmp: (x: T, y: T) => number): number {
  let lo = 0, hi = a.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (cmp(a[mid], target) < 0) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

lowerBound([1, 3, 3, 7], 3, (x, y) => x - y);   // 1
```

#### Binary search — Java

```java
static int lowerBound(int[] a, int target) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C#

```csharp
static int LowerBound(int[] a, int target) {
    int lo = 0, hi = a.Length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C

```c
#include <stddef.h>

size_t lower_bound(const int *a, size_t n, int target) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C++

```cpp
int lower_bound_index(const std::vector<int>& a, int target) {
    return int(std::lower_bound(a.begin(), a.end(), target) - a.begin());
}
```

#### Binary search — Go

```go
import (
	"cmp"
	"slices"
)

func lowerBound[T cmp.Ordered](a []T, target T) int {
	i, _ := slices.BinarySearch(a, target)   // earliest index with a[i] >= target
	return i
}

// Manual form with a predicate: sort.Search(len(a), func(i int) bool { return a[i] >= target })
```

#### Binary search — Rust

```rust
fn lower_bound(a: &[i32], target: i32) -> usize {
    a.partition_point(|&x| x < target)
}
```

#### Binary search — Ruby

```ruby
def lower_bound(a, target)
  a.bsearch_index { |x| x >= target } || a.size
end
```
