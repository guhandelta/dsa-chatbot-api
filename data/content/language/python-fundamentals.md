---
track: language
difficulty: Easy
language: python
category: Fundamentals
source: authored
io_mode: function
---
# Python fundamentals — Easy — Fundamentals

- **Paradigm and typing:** multi-paradigm; dynamic, strong typing; optional type hints (`list[int]`, `dict[str, int]`) are not enforced at runtime.
- **Execution and memory:** CPython compiles to bytecode and interprets it; reference counting plus a cycle-detecting garbage collector. Every value is a heap object; variables are references.
- **Integers and overflow:** `int` is arbitrary precision, so it never overflows. `float` is IEEE-754 double.
- **Division and modulo:** `/` returns float; `//` floors toward negative infinity (`-7 // 2 == -4`); `%` takes the sign of the divisor (`-7 % 3 == 2`).
- **Strings:** immutable `str` of Unicode code points; O(1) indexing; build with `"".join(parts)`, since repeated `+=` can be O(n²).
- **Equality:** `==` compares values via `__eq__`; `is` compares identity. Use `is` only for `None`.
- **Functions and recursion:** first-class functions, closures, lambdas, generators (`yield`). Default recursion limit is 1,000 frames; raise with `sys.setrecursionlimit`, or convert to an explicit stack.
- **Error handling:** exceptions with `try` / `except` / `finally`; `raise ValueError(...)`.
- **Iteration idioms:** `enumerate`, `zip`, `range`, comprehensions (`[x*x for x in a if x]`), unpacking (`a, b = b, a`), `sorted(key=...)`.
- **DSA pitfalls:** `[[0] * m] * n` aliases one row n times (use a comprehension); mutable default arguments (`def f(memo={})`) persist between calls; `list.pop(0)`, `list.insert(0, x)` and `x in list` are O(n).
