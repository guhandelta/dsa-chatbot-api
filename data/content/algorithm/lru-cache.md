---
track: algorithm
difficulty: Medium
algorithms: lru-cache
category: Data Structure
source: authored
io_mode: function
---
# LRU cache — Medium — Data Structure

An LRU cache evicts the least recently used entry when full. A hash map from key to list node gives O(1) lookup; a doubly linked list ordered by recency gives O(1) move-to-front and O(1) eviction from the tail. Built-in shortcuts: Python `OrderedDict` (or `@functools.lru_cache` for memoising functions), Java `LinkedHashMap` in access-order mode, and the insertion-ordered `Map` in JavaScript and TypeScript or `Hash` in Ruby (delete then re-insert moves a key to the end; the first key is the oldest). In C++ pair `std::list` with `std::unordered_map<K, std::list<...>::iterator>` and move nodes with `splice`; in C# pair `LinkedList<T>` with `Dictionary<K, LinkedListNode<T>>`; in Go pair `container/list` with `map[K]*list.Element` and call `MoveToFront`; in Rust use an index-based arena or the `lru` crate.

#### LRU cache — Python

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)
```

#### LRU cache — Java

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int cap;
    LRUCache(int cap) { super(16, 0.75f, true); this.cap = cap; }   // true = access order
    @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) { return size() > cap; }
}
```
