---
track: language
difficulty: Easy
language: python
category: Library & APIs
source: authored
io_mode: function
---
# Python data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `list` | `append`/`pop()` O(1) amortised; `insert(0, x)`/`pop(0)` O(n); growth ≈ 1.125× |
| Fixed / typed array | `array.array`, `tuple`, `bytearray` | Compact storage; tuple is immutable and hashable |
| Stack | `list` | `append`, `pop`, peek `s[-1]` |
| Queue / deque | `collections.deque` | `append`/`appendleft`/`pop`/`popleft` O(1); index access O(n) |
| Hash map | `dict` | Get/set/delete O(1) average; insertion-ordered (guaranteed 3.7+); `get(k, default)`, `setdefault` |
| Default map | `collections.defaultdict` | `defaultdict(list)` auto-creates missing values |
| Counter / multiset | `collections.Counter` | Counts in O(n); `most_common(k)` |
| Hash set | `set`, `frozenset` | Add/remove/membership O(1) average; `&`, `\|`, `-` set algebra |
| Priority queue | `heapq` on a `list` | Min-heap; `heappush`/`heappop` O(log n); `heapify` O(n); `nlargest(k, xs)` |
| Sorted list / map | Build, or third-party `sortedcontainers` (`SortedList`, `SortedDict`) | O(log n) insert and lookup in the package |
| Linked list | Build | `deque` covers most use cases |
| Bit set | `int` | Arbitrary-width bitmask |

| Algorithm | API |
| --- | --- |
| Sort | `sorted(xs, key=f, reverse=True)`, `xs.sort()`; Timsort, stable |
| Binary search | `bisect.bisect_left`, `bisect_right`, `insort` |
| Combinatorics | `itertools.permutations`, `combinations`, `product`, `accumulate` |
| Memoisation | `@functools.cache`, `@lru_cache(maxsize=n)` |
| Number theory | `math.gcd`, `math.lcm`, `math.comb`, `pow(b, e, mod)`, `math.isqrt` |
| Bits | `x.bit_count()`, `x.bit_length()` |
