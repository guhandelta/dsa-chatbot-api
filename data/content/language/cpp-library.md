---
track: language
difficulty: Easy
language: cpp
category: Library & APIs
source: authored
io_mode: function
---
# C++ data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `std::vector<T>` | `push_back`/`pop_back` O(1) amortised; `insert`/`erase` middle O(n); `reserve` pre-allocates |
| Fixed array | `std::array<T, N>` | Stack-allocated, bounds-checked `at()` |
| Deque | `std::deque<T>` | O(1) at both ends and O(1) indexing; chunked storage |
| Linked list | `std::list<T>`, `std::forward_list<T>` | O(1) insert/erase given an iterator; `splice` moves nodes in O(1) |
| Stack / queue | `std::stack`, `std::queue` | Adaptors over `deque` by default |
| Priority queue | `std::priority_queue<T>` | Max-heap by default; min-heap with `std::greater<T>` as the third template argument |
| Hash map / set | `std::unordered_map`, `std::unordered_set` | O(1) average; separate chaining; `max_load_factor` 1.0 |
| Sorted map / set | `std::map`, `std::set`, `std::multimap`, `std::multiset` (red-black trees) | O(log n); `lower_bound`, `upper_bound`, `equal_range` |
| Bit set | `std::bitset<N>`, `std::vector<bool>` | `count`, `test`, shifts |
| Non-owning views | `std::span<T>`, `std::string_view` | Slices without copies |

| Algorithm | API (`<algorithm>`, `<numeric>`, `<bit>`) |
| --- | --- |
| Sort | `std::sort` (introsort, unstable), `std::stable_sort`, `std::partial_sort`, `std::nth_element` (O(n) average selection) |
| Binary search | `std::lower_bound` (first ≥), `std::upper_bound` (first >), `std::equal_range`, `std::binary_search` |
| Permutations | `std::next_permutation`, `std::prev_permutation` |
| Sequence ops | `std::reverse`, `std::rotate`, `std::unique` (+ `erase`), `std::iota`, `std::accumulate`, `std::partial_sum` |
| Heap ops on a range | `std::make_heap`, `std::push_heap`, `std::pop_heap` |
| Number theory | `std::gcd`, `std::lcm` |
| Bits | `std::popcount`, `std::countr_zero`, `std::countl_zero`, `std::has_single_bit` |
