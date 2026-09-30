---
track: language
difficulty: Easy
language: rust
category: Library & APIs
source: authored
io_mode: function
---
# Rust data structures and algorithm APIs — Easy — Library & APIs

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Vec<T>` | `push`/`pop` O(1) amortised (`pop` returns `Option<T>`); `insert`/`remove` middle O(n); `swap_remove` O(1) |
| Fixed array | `[T; N]`, slices `&[T]` | Stack-allocated; slices borrow any contiguous range |
| Queue / deque | `VecDeque<T>` | Ring buffer; `push_back`/`pop_front` O(1) |
| Linked list | `LinkedList<T>` | Rarely the right choice; prefer `Vec` or `VecDeque` |
| Hash map / set | `HashMap<K,V>`, `HashSet<T>` | SwissTable, O(1) average; SipHash-1-3 default (DoS-resistant, slower); `entry(k).or_insert(v)` |
| Sorted map / set | `BTreeMap<K,V>`, `BTreeSet<T>` | B-tree, O(log n); `range(a..b)`, `first_key_value`, `last_key_value`, `pop_first` |
| Priority queue | `BinaryHeap<T>` | Max-heap; min-heap by wrapping items in `std::cmp::Reverse` |
| Shared ownership | `Rc<RefCell<T>>`, `Arc<Mutex<T>>` | Trees with parent links, shared graph nodes |
| Third-party | `indexmap`, `rustc-hash` (FxHash), `ahash`, `bitvec`, `lru` | Ordered maps, fast hashing, bit sets |

| Algorithm | API (slice methods) |
| --- | --- |
| Sort | `sort`, `sort_by_key` (stable); `sort_unstable`, `sort_unstable_by` (faster); floats via `sort_by(\|a, b\| a.total_cmp(b))` |
| Binary search | `binary_search` returns `Ok(index)` or `Err(insertion_point)`; `partition_point(pred)` for lower bound |
| Selection | `select_nth_unstable(k)` O(n) average |
| Sequence ops | `reverse`, `rotate_left`, `dedup`, `retain`, `windows(k)`, `chunks(k)`, `concat`, `iter().rev()` |
| Bits | `count_ones`, `trailing_zeros`, `leading_zeros`, `is_power_of_two` |
| Number theory | Build `gcd`, or crate `num` |
