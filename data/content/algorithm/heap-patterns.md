---
track: algorithm
difficulty: Easy
algorithms: heap-patterns
category: Data Structure
source: authored
io_mode: function
---
# Heap patterns: top K, merge K sorted lists, two heaps — Easy — Data Structure

- **Top K elements:** scan once while keeping a min-heap of size k; whenever it grows past k, pop the smallest. The heap ends with the k largest items and its root is the k-th largest, in O(n log k) time and O(k) space. Use a max-heap (or reversed comparator) for the k smallest. Problems: kth largest element, top K frequent elements, K closest points to origin.
- **Merge K sorted lists (k-way merge):** push the first element of each list with its list index; repeatedly pop the smallest, output it, and push the next element from the same list. N total elements cost O(N log k). Problems: merge k sorted lists, smallest range covering k lists, kth smallest in a sorted matrix.
- **Two heaps:** a max-heap holds the lower half and a min-heap the upper half, rebalanced after each insert so their sizes differ by at most one. The median is the larger heap's root, or the mean of both roots. Problems: find median from a data stream, sliding window median, maximise capital (IPO).

Put a unique tie-breaker (such as the list index) in heap tuples so equal keys never fall through to comparing incomparable payloads.

#### Top K, k-way merge and running median — Python

```python
import heapq

def kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)              # drop the smallest; keep the k largest
    return heap[0]

def merge_k_sorted(lists):                   # lists: sorted Python lists
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out

class MedianFinder:
    def __init__(self):
        self.low = []                        # max-heap of the lower half (negated values)
        self.high = []                       # min-heap of the upper half

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```
