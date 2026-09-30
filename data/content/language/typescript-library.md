---
track: language
difficulty: Easy
language: typescript
category: Library & APIs
source: authored
io_mode: function
---
# TypeScript data structures and algorithm APIs — Easy — Library & APIs

TypeScript runs on the JavaScript standard library, so costs match JavaScript; this chunk lists how each structure is typed and what must be built as a generic class.

| Structure | Type annotation | Key operations and notes |
| --- | --- | --- |
| Dynamic array / stack | `number[]`, `Array<T>`, `readonly T[]` | `push`/`pop` O(1) amortised; `readonly` blocks mutation at compile time |
| Tuple | `[number, number]`, `readonly [row: number, col: number]` | Fixed-length heterogeneous arrays; ideal for heap entries and edges |
| Typed array | `Int32Array`, `Float64Array` | Fixed-size numeric storage for DP tables |
| Queue / deque | Build a generic `Queue<T>` | Array with a head index gives O(1) dequeue |
| Hash map | `Map<K, V>` | O(1) average; `get` returns `V \| undefined`; object keys compare by reference |
| String-keyed record | `Record<string, V>` | Plain object; use only for string keys known at compile time |
| Hash set | `Set<T>` | O(1) average `has`, `add`, `delete` |
| Priority queue | Build a generic `Heap<T>` with a comparator | See the "Binary heap — TypeScript" chunk |
| Sorted map / set | Build | Balanced tree, or a sorted array with binary search |
| Linked list | Build `ListNode<T> { val: T; next: ListNode<T> \| null }` | — |
| Big integers | `bigint` | `123n` literals; cannot mix with `number` |

| Algorithm | API |
| --- | --- |
| Sort | `arr.sort((a, b) => a - b)` in place; `arr.toSorted(cmp)` returns a copy (requires `lib` ES2023); stable |
| Binary search | Build a generic `lowerBound<T>` with a comparator |
| Search | `indexOf`, `includes`, `find` (returns `T \| undefined`), `findIndex`, `findLast` |
| Aggregation | `reduce<U>(fn, init)`, `Object.groupBy` / `Map.groupBy` (requires `lib` ES2024) |
| Type utilities useful in DSA | `Readonly<T>`, `Partial<T>`, `Record<K, V>`, `ReturnType<F>`, `NonNullable<T>` |
