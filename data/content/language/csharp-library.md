---
track: language
difficulty: Easy
language: csharp
category: Library & APIs
source: authored
io_mode: function
---
# C# data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `List<T>` | `Add`/indexer O(1); `Insert(0, x)`/`RemoveAt(0)` O(n); growth 2× |
| Fixed array | `T[]`, `T[,]` (rectangular), `T[][]` (jagged) | Jagged arrays are usually faster |
| Stack | `Stack<T>` | `Push`/`Pop`/`Peek` O(1) |
| Queue | `Queue<T>` | `Enqueue`/`Dequeue`/`Peek` O(1); ring buffer |
| Deque | Build, or `LinkedList<T>` | .NET has no array deque |
| Linked list | `LinkedList<T>` (doubly linked) | `AddFirst`/`AddLast`/`Remove(node)` O(1) |
| Hash map | `Dictionary<K,V>` | O(1) average; `TryGetValue`, `TryAdd`, `GetValueOrDefault`; separate chaining in arrays |
| Hash set | `HashSet<T>` | O(1) average; `UnionWith`, `IntersectWith` |
| Sorted map | `SortedDictionary<K,V>` (red-black tree) | O(log n) insert and lookup |
| Sorted array map | `SortedList<K,V>` | O(log n) lookup, O(n) insert; index access |
| Sorted set | `SortedSet<T>` (red-black tree) | O(log n); `Min`, `Max`, `GetViewBetween(lo, hi)` for range queries |
| Priority queue | `PriorityQueue<TElement, TPriority>` (.NET 6+) | Min-heap by priority; `Enqueue`/`Dequeue` O(log n); no decrease-key; max-heap via reversed `Comparer` |
| Bit set | `BitArray` | Fixed-size bit vector |
| Concurrent | `ConcurrentDictionary`, `ConcurrentQueue` | Thread-safe variants |

| Algorithm | API |
| --- | --- |
| Sort | `Array.Sort` / `List<T>.Sort` introsort (unstable); LINQ `OrderBy`/`ThenBy` stable |
| Binary search | `Array.BinarySearch`, `List<T>.BinarySearch`; returns bitwise complement `~insertionPoint` when absent |
| Utilities | `Array.Fill`, `Array.Reverse`, `Span<T>.Sort` |
| Number theory | `BigInteger.GreatestCommonDivisor`, `BigInteger.ModPow` |
| Bits | `System.Numerics.BitOperations.PopCount`, `TrailingZeroCount`, `LeadingZeroCount` |
