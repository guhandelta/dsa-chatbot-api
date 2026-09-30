---
track: language
difficulty: Easy
language: javascript
category: Library & APIs
source: authored
io_mode: function
---
# JavaScript data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Array` | `push`/`pop` O(1) amortised; `shift`/`unshift`/`splice` O(n) |
| Typed array | `Int32Array`, `Float64Array`, `Uint8Array` | Fixed-size, contiguous, numeric only; fastest for DP tables |
| Queue / deque | Build | Array with a head index gives O(1) dequeue |
| Hash map | `Map` | `get`/`set`/`has`/`delete` O(1) average; insertion-ordered; any key type, objects by reference |
| Hash set | `Set` | `add`/`has`/`delete` O(1) average; insertion-ordered |
| Weak map / set | `WeakMap`, `WeakSet` | Object keys that do not prevent garbage collection; memo caches |
| Priority queue | Build | Binary heap class |
| Sorted map / set | Build | Balanced tree or sorted array with binary search |
| Linked list | Build | — |
| Big integers | `BigInt` | Arbitrary precision, `123n` literals |

| Algorithm | API |
| --- | --- |
| Sort | `arr.sort(cmp)` in place, `arr.toSorted(cmp)` copy; stable (ES2019+); numeric sort needs `(a, b) => a - b` |
| Binary search | Build |
| Search | `indexOf`, `includes`, `find`, `findIndex`, `findLast` |
| Aggregation | `reduce`, `Object.groupBy` / `Map.groupBy` (ES2024) |
| Bits | `Math.clz32`; popcount must be built |
