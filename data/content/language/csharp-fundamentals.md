---
track: language
difficulty: Easy
language: csharp
category: Fundamentals
source: authored
io_mode: function
---
# C# fundamentals — Easy — Fundamentals

- **Paradigm and typing:** object-oriented with strong functional features (LINQ, lambdas, pattern matching, records); static, strong typing; generics are reified, so `List<int>` stores unboxed ints.
- **Execution and memory:** compiles to IL, JIT- or AOT-compiled on .NET; generational garbage collector. `struct` types are value types (copied); `class` types are reference types. `Span<T>` gives allocation-free slices.
- **Integers and overflow:** `int` 32-bit, `long` 64-bit, plus unsigned `uint` / `ulong`; Nonconstant integral overflow follows the checked context and compiler configuration: unchecked arithmetic wraps, while checked arithmetic throws. Constant expressions also have compile-time overflow rules. `System.Numerics.BigInteger` is arbitrary precision.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; For a positive divisor `b`, compute `r = a % b` and add `b` only when `r < 0`; adding `b` unconditionally can overflow a fixed-width type.
- **Strings:** immutable `string` (UTF-16); build with `StringBuilder`; `ReadOnlySpan<char>` for substring work without copying.
- **Equality:** `==` compares values for primitives, strings and records, and references for ordinary classes unless overloaded; `Equals` and `GetHashCode` must be overridden together.
- **Functions and recursion:** methods, lambdas, delegates (`Func<T, TResult>`), local functions, iterators (`yield return`). Stack capacity depends on the runtime, operating system and thread configuration; do not assume a portable recursion depth. Prefer an explicit traversal stack when input depth is unbounded.
- **Error handling:** unchecked exceptions only; `try` / `catch` / `finally`; `using` for disposal.
- **Iteration idioms:** `foreach`, LINQ (`nums.Where(x => x > 0).Select(x => x * x)`), tuples and deconstruction (`(a, b) = (b, a)`), ranges and indices (`arr[^1]`, `arr[1..3]`).
- **DSA pitfalls:** LINQ cost depends on the operators, enumeration and materialization; inspect allocations and repeated enumeration rather than assuming every query has the same overhead; `List<T>.RemoveAt(0)` is O(n); `Dictionary` indexer throws `KeyNotFoundException` on a missing key, so use `TryGetValue`; `SortedList<K,V>` inserts are O(n) (use `SortedDictionary` for many inserts).

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/arithmetic-operators
