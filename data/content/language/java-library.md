---
track: language
difficulty: Easy
language: java
category: Library & APIs
source: authored
io_mode: function
---
# Java data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `ArrayList<T>` | `add`/`get` O(1); `add(0, x)`/`remove(0)` O(n); growth 1.5× |
| Fixed array | `int[]`, `T[]` | Primitive arrays avoid boxing |
| Stack / queue / deque | `ArrayDeque<T>` | `push`/`pop`, `offer`/`poll`, `offerFirst`/`pollLast` O(1); no nulls |
| Linked list | `LinkedList<T>` | O(1) at ends; O(n) indexed access |
| Hash map | `HashMap<K,V>` | O(1) average; chained buckets become red-black trees at 8 entries; load factor 0.75 |
| Insertion / access-ordered map | `LinkedHashMap<K,V>` | Access-order mode plus `removeEldestEntry` gives an LRU cache |
| Hash set | `HashSet<T>` | O(1) average |
| Sorted map / set | `TreeMap`, `TreeSet` (red-black trees) | O(log n); `floorKey`, `ceilingKey`, `headMap`, `subMap`, `firstKey`, `pollFirst` |
| Priority queue | `PriorityQueue<T>` | Min-heap by default; `offer`/`poll` O(log n); `remove(Object)` O(n); max-heap via `Comparator.reverseOrder()` |
| Bit set | `BitSet` | `set`, `get`, `cardinality`, `nextSetBit` |
| Concurrent | `ConcurrentHashMap`, `ConcurrentSkipListMap`, `ConcurrentLinkedQueue` | Thread-safe variants |

| Algorithm | API |
| --- | --- |
| Sort | `Arrays.sort(int[])` dual-pivot quicksort (unstable); `Arrays.sort(T[])` / `Collections.sort` Timsort (stable); `list.sort(Comparator.comparing(P::age).reversed())` |
| Binary search | `Arrays.binarySearch`, `Collections.binarySearch`; returns `-(insertionPoint) - 1` when absent |
| Utilities | `Arrays.fill`, `Arrays.copyOfRange`, `Collections.reverse`, `Collections.swap` |
| Number theory | `BigInteger.gcd`, `BigInteger.modPow`, `Math.floorMod` |
| Bits | `Integer.bitCount`, `numberOfTrailingZeros`, `numberOfLeadingZeros`, `highestOneBit` |
