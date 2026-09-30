---
track: algorithm
difficulty: Medium
algorithms: merge-sort
category: Algorithm
source: authored
io_mode: function
---
# Merge sort — Medium — Algorithm

Merge sort splits the array in half, sorts each half recursively, then merges the two sorted halves by repeatedly taking the smaller front element. The recursion depth is log n and each level does O(n) merging work. It is stable and has no bad inputs, but needs O(n) auxiliary space. Counting inversions is a small extension: when an element from the right half is taken, add the number of elements left in the left half.

#### Merge sort — Python

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]
```

#### Merge sort — JavaScript

```javascript
function mergeSort(a) {
  if (a.length <= 1) return a;
  const mid = a.length >> 1;
  const l = mergeSort(a.slice(0, mid)), r = mergeSort(a.slice(mid));
  const out = []; let i = 0, j = 0;
  while (i < l.length && j < r.length) out.push(l[i] <= r[j] ? l[i++] : r[j++]);
  return out.concat(l.slice(i), r.slice(j));
}
```

#### Merge sort — TypeScript

```typescript
function mergeSort<T>(a: readonly T[], cmp: (x: T, y: T) => number): T[] {
  if (a.length <= 1) return a.slice();
  const mid = a.length >> 1;
  const l = mergeSort(a.slice(0, mid), cmp);
  const r = mergeSort(a.slice(mid), cmp);
  const out: T[] = [];
  let i = 0, j = 0;
  while (i < l.length && j < r.length) out.push(cmp(l[i], r[j]) <= 0 ? l[i++] : r[j++]);
  return out.concat(l.slice(i), r.slice(j));
}

const sorted = mergeSort([5, 2, 9, 1], (x, y) => x - y);   // [1, 2, 5, 9]
```

#### Merge sort — Java

```java
static void mergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    mergeSort(a, tmp, lo, mid); mergeSort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo);
}
```

#### Merge sort — C#

```csharp
static void MergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    MergeSort(a, tmp, lo, mid); MergeSort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    Array.Copy(tmp, lo, a, lo, hi - lo);
}
```

#### Merge sort — C

```c
#include <string.h>

void merge_sort(int *a, int *tmp, int lo, int hi) {         /* sorts a[lo, hi) */
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, tmp, lo, mid); merge_sort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    memcpy(a + lo, tmp + lo, (hi - lo) * sizeof *a);
}
```

#### Merge sort — C++

```cpp
void merge_sort(std::vector<int>& a, std::vector<int>& tmp, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, tmp, lo, mid); merge_sort(a, tmp, mid, hi);
    std::merge(a.begin() + lo, a.begin() + mid, a.begin() + mid, a.begin() + hi, tmp.begin() + lo);
    std::copy(tmp.begin() + lo, tmp.begin() + hi, a.begin() + lo);
}
```

#### Merge sort — Go

```go
// mergeSort sorts a in place; tmp must have len(tmp) >= len(a).
func mergeSort(a, tmp []int) {
	n := len(a)
	if n < 2 {
		return
	}
	mid := n / 2
	mergeSort(a[:mid], tmp)
	mergeSort(a[mid:], tmp)
	i, j, k := 0, mid, 0
	for i < mid && j < n {
		if a[i] <= a[j] {
			tmp[k] = a[i]
			i++
		} else {
			tmp[k] = a[j]
			j++
		}
		k++
	}
	k += copy(tmp[k:], a[i:mid])
	copy(tmp[k:], a[j:])
	copy(a, tmp[:n])
}

// Usage: mergeSort(nums, make([]int, len(nums)))
```

#### Merge sort — Rust

```rust
fn merge_sort<T: PartialOrd + Copy>(a: &mut [T]) {
    let n = a.len();
    if n < 2 { return; }
    let mid = n / 2;
    merge_sort(&mut a[..mid]);
    merge_sort(&mut a[mid..]);
    let mut out = Vec::with_capacity(n);
    let (mut i, mut j) = (0, mid);
    while i < mid && j < n {
        if a[i] <= a[j] { out.push(a[i]); i += 1; } else { out.push(a[j]); j += 1; }
    }
    out.extend_from_slice(&a[i..mid]);
    out.extend_from_slice(&a[j..]);
    a.copy_from_slice(&out);
}
```

#### Merge sort — Ruby

```ruby
def merge_sort(a)
  return a if a.size <= 1
  mid = a.size / 2
  left, right = merge_sort(a[0...mid]), merge_sort(a[mid..])
  out, i, j = [], 0, 0
  while i < left.size && j < right.size
    if left[i] <= right[j]
      out << left[i]; i += 1
    else
      out << right[j]; j += 1
    end
  end
  out.concat(left[i..], right[j..])
end
```
