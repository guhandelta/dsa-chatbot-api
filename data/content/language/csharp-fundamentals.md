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
- **Integers and overflow:** `int` 32-bit, `long` 64-bit, plus unsigned `uint` / `ulong`; overflow wraps by default and throws inside a `checked { }` block. `System.Numerics.BigInteger` is arbitrary precision.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; use `((a % b) + b) % b` for a non-negative result.
- **Strings:** immutable `string` (UTF-16); build with `StringBuilder`; `ReadOnlySpan<char>` for substring work without copying.
- **Equality:** `==` compares values for primitives, strings and records, and references for ordinary classes unless overloaded; `Equals` and `GetHashCode` must be overridden together.
- **Functions and recursion:** methods, lambdas, delegates (`Func<T, TResult>`), local functions, iterators (`yield return`). The main thread stack is 1 MB on Windows and follows ulimit -s (usually 8 MB) on Linux; deep recursion risks `StackOverflowException`, which cannot be caught.
- **Error handling:** unchecked exceptions only; `try` / `catch` / `finally`; `using` for disposal.
- **Iteration idioms:** `foreach`, LINQ (`nums.Where(x => x > 0).Select(x => x * x)`), tuples and deconstruction (`(a, b) = (b, a)`), ranges and indices (`arr[^1]`, `arr[1..3]`).
- **DSA pitfalls:** LINQ in hot loops allocates and is slower than plain loops; `List<T>.RemoveAt(0)` is O(n); `Dictionary` indexer throws `KeyNotFoundException` on a missing key, so use `TryGetValue`; `SortedList<K,V>` inserts are O(n) (use `SortedDictionary` for many inserts).
