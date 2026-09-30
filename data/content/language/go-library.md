---
track: language
difficulty: Easy
language: go
category: Library & APIs
source: authored
io_mode: function
---
# Go data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | slice `[]T` | `append` O(1) amortised (growth 2× below 256 elements, tapering toward 1.25×); pop with `s = s[:len(s)-1]`; `slices.Insert` / `slices.Delete` O(n) |
| Fixed array | `[N]T` | Value type: copied on assignment, comparable, usable as a map key |
| Queue | slice with `q = q[1:]` | O(1) dequeue, but the backing array is only released after `append` reallocates; a head index avoids repeated reslicing |
| Deque / linked list | `container/list` (doubly linked, `any` values) | `PushFront`, `PushBack`, `Remove`, `MoveToFront` O(1); needs type assertions |
| Circular list | `container/ring` | Fixed-size ring of `any` values |
| Hash map | `map[K]V` | O(1) average; `v, ok := m[k]`, `delete(m, k)`, `clear(m)`; Swiss tables since Go 1.24; iteration order randomised |
| Hash set | `map[T]struct{}` | Zero-byte values; `_, ok := set[x]` |
| Priority queue | `container/heap` over a type implementing `heap.Interface` | `heap.Init` O(n), `heap.Push` / `heap.Pop` O(log n), `heap.Fix` after changing a priority |
| Sorted map / set | Build, or third-party `github.com/google/btree` | Sorted slice + `slices.BinarySearch` for small sizes |
| Bit set | Build with `[]uint64`, or `math/big.Int` `SetBit` / `Bit` | — |
| Big integers | `math/big` (`big.Int`, `big.Rat`) | Arbitrary precision |
| Concurrent | channels, `sync.Mutex`, `sync.Map` | Goroutine-safe queues and maps |

| Algorithm | API |
| --- | --- |
| Sort | `slices.Sort` (pdqsort, unstable), `slices.SortFunc(s, cmp)`, `slices.SortStableFunc`; older `sort.Slice`, `sort.SliceStable`, `sort.Ints` |
| Binary search | `slices.BinarySearch(s, x)` returns `(insertionIndex, found)`; `sort.Search(n, pred)` returns the first index where `pred` is true |
| Comparison | `cmp.Compare`, `cmp.Less`, `cmp.Or` (chain tie-breakers) |
| Sequence ops | `slices.Reverse`, `slices.Contains`, `slices.Index`, `slices.Max`, `slices.Min`, `slices.Compact`, `slices.Equal`, built-in `copy`, `min`, `max` |
| Number theory | `new(big.Int).GCD`, `new(big.Int).Exp(b, e, m)` for modular power; build `gcd` for plain `int` |
| Bits | `math/bits.OnesCount64`, `TrailingZeros64`, `LeadingZeros64`, `Len64` |
