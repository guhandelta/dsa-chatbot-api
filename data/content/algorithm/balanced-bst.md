---
track: algorithm
difficulty: Easy
algorithms: balanced-bst
category: Data Structure
source: authored
io_mode: function
---
# Balanced search trees and ordered maps — Easy — Data Structure

Self-balancing trees keep height O(log n) under any insertion order and support ordered queries (floor, ceiling, range) that hash tables cannot.

| Tree | Balance rule | Trade-off | Used by |
| --- | --- | --- | --- |
| Red-black tree | No red node has a red child; every root-to-leaf path has equal black nodes | Fewer rotations, faster writes | Java `TreeMap`, C# `SortedDictionary`/`SortedSet`, C++ `std::map`/`std::set` |
| AVL tree | Subtree heights differ by at most 1 | Stricter balance, faster reads | Read-heavy indexes |
| B-tree | Each node holds many sorted keys; all leaves at the same depth | Cache- and disk-friendly | Rust `BTreeMap`/`BTreeSet`, database and filesystem indexes |

Ordered queries in languages that ship a sorted map (Python, JavaScript, TypeScript, Go and Ruby need a sorted array with binary search or a third-party package):

| Query | Java `TreeMap` | C# `SortedSet` | C++ `std::map` | Rust `BTreeMap` |
| --- | --- | --- | --- | --- |
| Smallest key ≥ x | `ceilingKey(x)` | `GetViewBetween(x, max).Min` | `lower_bound(x)` | `range(x..).next()` |
| Largest key ≤ x | `floorKey(x)` | `GetViewBetween(min, x).Max` | `prev(upper_bound(x))` | `range(..=x).next_back()` |
| Min / max | `firstKey()` / `lastKey()` | `Min` / `Max` | `begin()` / `rbegin()` | `first_key_value()` / `last_key_value()` |
| Keys in \[a, b) | `subMap(a, b)` | `GetViewBetween(a, b)` (inclusive) | `lower_bound(a)` to `lower_bound(b)` | `range(a..b)` |
