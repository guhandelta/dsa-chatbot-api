---
track: algorithm
difficulty: Medium
algorithms: insertion-sort-heap-sort
category: Algorithm
source: authored
io_mode: function
---
# Insertion sort and heap sort — Medium — Algorithm

Insertion sort shifts each element left until it is in place; it is the fastest choice for tiny or nearly sorted arrays, which is why hybrid sorts (Timsort, introsort) use it for small runs. Heap sort builds a max-heap in O(n), then repeatedly swaps the maximum to the end and sifts down, giving guaranteed O(n log n) with O(1) extra space.

#### Insertion sort and heap sort — Python

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0 and a[j] > x:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = x

def heap_sort(a):
    def sift(i, n):
        while (c := 2 * i + 1) < n:
            if c + 1 < n and a[c + 1] > a[c]:
                c += 1
            if a[i] >= a[c]:
                return
            a[i], a[c] = a[c], a[i]; i = c
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(0, end)
```
