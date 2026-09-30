---
track: algorithm
difficulty: Medium
algorithms: sorting-comparison
category: Algorithm
source: authored
io_mode: function
---
# Sorting algorithm comparison — Medium — Algorithm

Comparison sorts cannot beat O(n log n) in the worst case; counting and radix sort beat it by exploiting small integer keys. A stable sort keeps equal keys in their original order, which matters when sorting by several keys in sequence.

| Algorithm | Best | Average | Worst | Extra space | Stable | Use when |
| --- | --- | --- | --- | --- | --- | --- |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | Yes | n < \~16, nearly sorted data |
| Selection sort | O(n²) | O(n²) | O(n²) | O(1) | No | Minimising swaps |
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Teaching only |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Linked lists, external sorting, stability required |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) | No | General in-memory sorting with random pivots |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No | Guaranteed O(n log n) with O(1) space |
| Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes | Integer keys in a small range k |
| Radix sort (LSD) | O(d(n + b)) | O(d(n + b)) | O(d(n + b)) | O(n + b) | Yes | Fixed-width integers or strings, d digits in base b |
| Timsort | O(n) | O(n log n) | O(n log n) | O(n) | Yes | Real-world data with runs (Python, Java objects, V8) |
| Introsort | O(n log n) | O(n log n) | O(n log n) | O(log n) | No | Quicksort that falls back to heap sort (C++ `std::sort`, .NET `Array.Sort`) |
| Pattern-defeating quicksort | O(n) | O(n log n) | O(n log n) | O(log n) | No | Go `slices.Sort` and `sort.Slice`; Rust `sort_unstable` uses ipnsort, a pdqsort descendant |
