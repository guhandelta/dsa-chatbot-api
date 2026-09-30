---
track: algorithm
difficulty: Medium
algorithms: quicksort
category: Algorithm
source: authored
io_mode: function
---
# Quicksort — Medium — Algorithm

Quicksort picks a pivot, partitions the array so smaller elements come before it and larger ones after, then recurses on both sides. A random pivot makes the O(n²) worst case (already-sorted input with a first-element pivot) vanishingly unlikely. It sorts in place and is not stable. The Lomuto partition below is the clearest; Hoare partition does about three times fewer swaps, and three-way partitioning (Dutch national flag) handles many duplicate keys in O(n). Recursing into the smaller side first bounds stack depth at O(log n).

#### Quicksort — Python

```python
import random

def quicksort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]
    quicksort(a, lo, i - 1)
    quicksort(a, i + 1, hi)
```

#### Quicksort — JavaScript

```javascript
function quicksort(a, lo = 0, hi = a.length - 1) {
  if (lo >= hi) return;
  const r = lo + Math.floor(Math.random() * (hi - lo + 1));
  [a[r], a[hi]] = [a[hi], a[r]];
  const pivot = a[hi]; let i = lo;
  for (let j = lo; j < hi; j++) if (a[j] < pivot) { [a[i], a[j]] = [a[j], a[i]]; i++; }
  [a[i], a[hi]] = [a[hi], a[i]];
  quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — TypeScript

```typescript
function quicksort<T>(a: T[], cmp: (x: T, y: T) => number, lo = 0, hi = a.length - 1): void {
  if (lo >= hi) return;
  const r = lo + Math.floor(Math.random() * (hi - lo + 1));
  [a[r], a[hi]] = [a[hi], a[r]];
  const pivot = a[hi];
  let i = lo;
  for (let j = lo; j < hi; j++) {
    if (cmp(a[j], pivot) < 0) {
      [a[i], a[j]] = [a[j], a[i]];
      i++;
    }
  }
  [a[i], a[hi]] = [a[hi], a[i]];
  quicksort(a, cmp, lo, i - 1);
  quicksort(a, cmp, i + 1, hi);
}

const nums = [5, 2, 9, 1];
quicksort(nums, (x, y) => x - y);   // nums is now [1, 2, 5, 9]
```

#### Quicksort — Java

```java
static void quicksort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int r = java.util.concurrent.ThreadLocalRandom.current().nextInt(lo, hi + 1);
    int t = a[r]; a[r] = a[hi]; a[hi] = t;
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) { t = a[i]; a[i] = a[j]; a[j] = t; i++; }
    t = a[i]; a[i] = a[hi]; a[hi] = t;
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — C#

```csharp
static void QuickSort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int r = Random.Shared.Next(lo, hi + 1);
    (a[r], a[hi]) = (a[hi], a[r]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) { (a[i], a[j]) = (a[j], a[i]); i++; }
    (a[i], a[hi]) = (a[hi], a[i]);
    QuickSort(a, lo, i - 1); QuickSort(a, i + 1, hi);
}
```

#### Quicksort — C

```c
#include <stdlib.h>

static void swap_int(int *x, int *y) { int t = *x; *x = *y; *y = t; }

void quicksort(int *a, int lo, int hi) {
    if (lo >= hi) return;
    swap_int(&a[lo + rand() % (hi - lo + 1)], &a[hi]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) swap_int(&a[i++], &a[j]);
    swap_int(&a[i], &a[hi]);
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — C++

```cpp
void quicksort(std::vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    static std::mt19937 rng(std::random_device{}());
    std::swap(a[std::uniform_int_distribution<int>(lo, hi)(rng)], a[hi]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; ++j) if (a[j] < pivot) std::swap(a[i++], a[j]);
    std::swap(a[i], a[hi]);
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — Go

```go
import "math/rand/v2"

func quicksort(a []int) {
	if len(a) < 2 {
		return
	}
	hi := len(a) - 1
	r := rand.IntN(len(a))
	a[r], a[hi] = a[hi], a[r]
	pivot, i := a[hi], 0
	for j := 0; j < hi; j++ {
		if a[j] < pivot {
			a[i], a[j] = a[j], a[i]
			i++
		}
	}
	a[i], a[hi] = a[hi], a[i]
	quicksort(a[:i])     // sub-slices share the backing array, so sorting is in place
	quicksort(a[i+1:])
}
```

#### Quicksort — Rust

```rust
fn quicksort<T: PartialOrd>(a: &mut [T]) {
    let n = a.len();
    if n < 2 { return; }
    a.swap(n / 2, n - 1);                 // middle pivot; std has no RNG, use the rand crate for random
    let mut i = 0;
    for j in 0..n - 1 {
        if a[j] < a[n - 1] { a.swap(i, j); i += 1; }
    }
    a.swap(i, n - 1);
    let (left, right) = a.split_at_mut(i);
    quicksort(left);
    quicksort(&mut right[1..]);
}
```

#### Quicksort — Ruby

```ruby
def quicksort(a, lo = 0, hi = a.size - 1)
  return a if lo >= hi
  r = rand(lo..hi)
  a[r], a[hi] = a[hi], a[r]
  pivot, i = a[hi], lo
  (lo...hi).each do |j|
    next unless a[j] < pivot
    a[i], a[j] = a[j], a[i]
    i += 1
  end
  a[i], a[hi] = a[hi], a[i]
  quicksort(a, lo, i - 1)
  quicksort(a, i + 1, hi)
  a
end
```
