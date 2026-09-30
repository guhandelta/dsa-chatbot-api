---
track: language
difficulty: Easy
language: c
category: Fundamentals
source: authored
io_mode: function
---
# C fundamentals — Easy — Fundamentals

- **Paradigm and typing:** procedural; static, weak typing with implicit conversions; no generics (use `void *` plus element size, or macros).
- **Execution and memory:** compiled to native code; manual memory management with `malloc` / `calloc` / `realloc` / `free`. Locals live on the stack (typically 1–8 MB); arrays decay to pointers when passed to functions, so length is passed separately.
- **Integers and overflow:** sizes are platform-defined; use `<stdint.h>` (`int32_t`, `int64_t`, `uint64_t`). Signed overflow is undefined behaviour; unsigned overflow wraps modulo 2ⁿ.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; division by zero is undefined behaviour.
- **Strings:** `char` arrays terminated by `'\0'`; `strlen` is O(n); use `snprintf` and `strncpy` over unbounded `sprintf` and `strcpy`.
- **Equality:** `==` compares scalars and pointer addresses; compare strings with `strcmp` and memory with `memcmp`; structs cannot be compared with `==`.
- **Functions and recursion:** function pointers enable callbacks (`qsort` comparators); no closures. Recursion depth is limited only by stack size; no guaranteed tail-call optimisation.
- **Error handling:** return codes, `errno`, and `NULL` pointers; no exceptions.
- **Iteration idioms:** index loops `for (size_t i = 0; i < n; i++)`, pointer walking `for (int *p = a; p < a + n; p++)`.
- **DSA pitfalls:** every allocation needs a matching `free` and a `NULL` check; large local arrays overflow the stack (allocate statically or on the heap); `qsort` comparators should return `(a > b) - (a < b)`, not `a - b`; test with `-fsanitize=address,undefined`.
