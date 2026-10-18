---
track: algorithm
difficulty: Hard
algorithms: skip-list
category: Data Structure
source: authored
io_mode: function
---
# Skip list — Hard — Data Structure

A skip list is a sorted linked list with extra levels of forward pointers. Each node is promoted to the next level with probability 1/2, so higher levels act as express lanes and a search drops down level by level in O(log n) expected time. It is simpler than a balanced tree to make lock-free, which is why Redis sorted sets and Java's `ConcurrentSkipListMap` use it.

## Algorithms

Each chunk explains one algorithm, its complexity and when to use it; anchor algorithms carry code in all ten languages.
