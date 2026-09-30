---
track: language
difficulty: Easy
language: ruby
category: Library & APIs
source: authored
io_mode: function
---
# Ruby data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Array` | `push`/`<<`/`pop` O(1) amortised; `insert(0, x)` O(n); negative indexing `a[-1]` |
| Queue / deque | `Array` | `shift` and `unshift` are O(1) amortised in CRuby (shared-array optimisation), so an Array works as a deque; `Thread::Queue` for threads |
| Hash map | `Hash` | O(1) average; open addressing; insertion-ordered; `Hash.new(0)` for counters; `fetch(k, default)`, `dig`, `group_by`, `tally` |
| Hash set | `Set` | O(1) average membership; autoloaded since Ruby 3.2 (`require "set"` before) |
| Priority queue | Build | Binary heap class |
| Sorted map / set | Build, or gems `rbtree`, `algorithms` | Sorted `Array` + `bsearch_index` for small sizes |
| Linked list | Build | — |
| Records | `Struct`, `Data.define` (3.2+) | Lightweight node and point types |
| Big integers | `Integer` | Arbitrary precision built in |

| Algorithm | API |
| --- | --- |
| Sort | `sort`, `sort!`, `sort_by { \|x\| -x.age }`, `min_by`, `max_by`, `max(k)`; quicksort-based, not stable (stabilise with `sort_by.with_index { \|x, i\| [key(x), i] }`) |
| Binary search | `bsearch { \|x\| x >= target }` (find-minimum mode), `bsearch_index` |
| Combinatorics | `permutation(k)`, `combination(k)`, `product`, `repeated_combination` |
| Enumerable | `each_cons(k)` sliding window, `each_slice(k)`, `each_with_object`, `inject(:+)`, `sum`, `tally`, `partition`, `chunk_while` |
| Number theory | `Integer#gcd`, `lcm`, `pow(e, mod)`, `Integer.sqrt`, `Prime` library (gem since 3.1) |
| Bits | `x.bit_length`, `x[i]` reads bit i, `x.to_s(2).count("1")` for popcount |

## Data structures

Each chunk defines one structure, its operation costs, when to choose it, and a reference implementation.
