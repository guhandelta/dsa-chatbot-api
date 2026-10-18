---
track: design-patterns
difficulty: Easy
patterns: iterator
category: Behavioural
source: generated-gap-fill
io_mode: function
review_status: source_linked_not_expert_certified
generated_on: 2026-10-18
---
# Iterator — Easy — Behavioural

## Problem
Code should traverse a collection without knowing how it is stored, and a collection may offer several traversal orders.

## When to reach for it
Custom data structures (trees, graphs, ranges, paginated results) that should work with the language's loops and library functions. Providing an iterator lets callers use `for` loops, comprehensions and standard algorithms.

## When NOT to
When a collection is already a standard type, use its built-in iteration; wrapping it adds nothing.

## Language notes
- **Python** — implement `__iter__`, usually as a generator function with `yield`; see the Python iterators reference.
- **JavaScript** — implement `[Symbol.iterator]`, often with a generator function `*[Symbol.iterator]()`.
- **Java** — implement `Iterable<T>` returning an `Iterator<T>`; streams for pipelines.
- **C#** — implement `IEnumerable<T>` with `yield return`.
- **Rust** — implement `Iterator` (`fn next(&mut self) -> Option<Item>`), and `IntoIterator` for `for` loops; adapters such as `map` and `filter` come free.
- **Go** — Go 1.23 range-over-func iterators (`iter.Seq[T]`); earlier code used callbacks or channels.
- **C++** — iterator types satisfying the iterator concepts, or C++20 ranges and C++23 `std::generator`.
- **Ruby** — define `each` and include `Enumerable`.

## Watchouts
- Modifying a collection while iterating over it is undefined, an error, or silently wrong depending on the language; see each language's reference.
- Lazy iterators can be consumed only once in many languages.
- Iterators holding locks or file handles need a way to close them early.
