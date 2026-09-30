---
track: language
difficulty: Easy
language: ruby
category: Fundamentals
source: authored
io_mode: function
---
# Ruby fundamentals — Easy — Fundamentals

- **Paradigm and typing:** pure object-oriented (every value is an object, including integers and `nil`) with functional blocks; dynamic, strong typing with duck typing; optional RBS type signatures.
- **Execution and memory:** interpreted by CRuby's YARV virtual machine, with the optional YJIT compiler; generational, incremental garbage collector. Variables hold references.
- **Integers and overflow:** `Integer` is arbitrary precision and never overflows; `Float` is IEEE-754 double; `Rational` for exact fractions.
- **Division and modulo:** integer `/` floors toward negative infinity (`-7 / 2 == -4`); `%` takes the sign of the divisor (`-7 % 3 == 2`); `fdiv` returns a float.
- **Strings:** mutable `String` (UTF-8 by default); `<<` appends in place, while `+` allocates a new string; `freeze` makes a string immutable; symbols (`:name`) are immutable interned identifiers, ideal as hash keys.
- **Equality:** `==` compares values; `equal?` compares identity; `eql?` is used by `Hash` (so `1.eql?(1.0)` is false); `<=>` is the three-way comparison used by sorting.
- **Functions and recursion:** methods, blocks (`{ |x| ... }`), procs and lambdas; `yield` calls the block. Default recursion depth is roughly 10,000 frames (`SystemStackError` beyond); tail-call optimisation is off by default.
- **Error handling:** `begin` / `rescue` / `ensure`; `raise ArgumentError, "msg"`.
- **Iteration idioms:** `each`, `each_with_index`, `map`, `select`, `reduce` / `inject`, `times`, `upto`, `each_cons(k)` for sliding windows, `each_slice(k)` for chunks, parallel assignment (`a, b = b, a`).
- **DSA pitfalls:** `Array.new(n, [])` shares one inner array (use `Array.new(n) { [] }`); `Hash.new([])` shares one default array (use `Hash.new { |h, k| h[k] = [] }`); `array.shift` is O(1) amortised in CRuby but `array.delete_at(0)` in loops is not; `array.include?` is O(n), so use `Set`.

## Language data structures and algorithm APIs

Each chunk lists what one language's standard library provides, with the calls to use and their cost; "Build" means no standard type exists.
