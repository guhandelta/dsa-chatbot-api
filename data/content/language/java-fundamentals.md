---
track: language
difficulty: Easy
language: java
category: Fundamentals
source: authored
io_mode: function
---
# Java fundamentals — Easy — Fundamentals

- **Paradigm and typing:** class-based object-oriented with functional features (lambdas, streams, records, sealed types); static, strong typing; generics are type-erased at runtime.
- **Execution and memory:** compiles to JVM bytecode, JIT-compiled at runtime; garbage collected (G1 by default). Primitives (`int`, `long`, `double`, `char`, `boolean`) live by value; everything else is a reference.
- **Integers and overflow:** `int` is 32-bit, `long` 64-bit, both signed two's complement; overflow wraps silently. `Math.addExact` throws on overflow; `BigInteger` is arbitrary precision.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; `Math.floorMod(a, b)` gives a non-negative result for positive b.
- **Strings:** immutable `String` (UTF-16); `charAt(i)` is O(1); build with `StringBuilder`; `s.toCharArray()` for in-place work.
- **Equality:** `==` compares primitives by value and objects by reference; use `.equals` for objects. `Integer` values outside −128..127 are distinct objects, so `==` on boxed integers is a common bug.
- **Functions and recursion:** methods live in classes; lambdas implement functional interfaces (`Function`, `Comparator`). Recursion capacity depends on the JVM, thread kind, stack configuration and frame size. An explicit traversal stack avoids relying on an assumed recursive depth; a requested platform-thread stack size is implementation-dependent.
- **Error handling:** checked and unchecked exceptions; `try` / `catch` / `finally`, try-with-resources.
- **Iteration idioms:** enhanced `for (int x : arr)`, `IntStream.range`, streams (`list.stream().filter(...).toList()`), `var` for local type inference.
- **DSA pitfalls:** comparator by subtraction (`(a, b) -> a - b`) overflows, so use `Integer.compare`; boxing in `List<Integer>` costs memory and speed; avoid legacy `Stack`, `Vector` and `Hashtable`.

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html
