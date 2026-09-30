---
track: language
difficulty: Easy
language: cpp
category: Fundamentals
source: authored
io_mode: function
---
# C++ fundamentals — Easy — Fundamentals

- **Paradigm and typing:** multi-paradigm (procedural, object-oriented, generic, functional); static typing with implicit numeric conversions; templates and C++20 concepts provide compile-time generics.
- **Execution and memory:** compiled to native code; value semantics by default; RAII ties resource lifetime to scope. Smart pointers (`std::unique_ptr`, `std::shared_ptr`) replace manual `new` / `delete`; move semantics avoid copies.
- **Integers and overflow:** same as C: use `int64_t` / `long long` for large values; signed overflow is undefined behaviour; unsigned wraps.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend.
- **Strings:** mutable `std::string` of bytes; `std::string_view` for non-owning slices; `+=` with `reserve` for building.
- **Equality:** `==` compares values for standard types; custom types define `operator==`, or `= default` the C++20 `operator<=>` for all comparisons.
- **Functions and recursion:** free functions, member functions, lambdas with captures (`[&]`, `[=]`), `std::function`. Recursion depth limited by stack size; recursive lambdas need `std::function` or C++23 deducing `this`.
- **Error handling:** exceptions (`throw`, `try`, `catch`), `std::optional` and `std::expected` (C++23) for recoverable failures.
- **Iteration idioms:** range-for `for (auto& x : v)`, structured bindings `auto [k, v] = pair`, `<algorithm>` and C++20 ranges (`std::ranges::sort(v)`).
- **DSA pitfalls:** `map[key]` inserts a default when missing (use `find` or `contains`); `vector` growth invalidates iterators, pointers and references; `v.size() - 1` wraps when empty because `size()` is unsigned; comparators must be strict weak orderings (`<`, not `<=`); `unordered_map` with default hashing can be attacked by crafted keys.
