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
- **Execution and memory:** compiled to native code; manual memory management with `malloc` / `calloc` / `realloc` / `free`. Automatic storage is commonly implemented with a stack, but C does not prescribe a stack size or physical placement for every local. Array parameters are adjusted to pointer types, so pass the required length separately.
- **Integers and overflow:** sizes are platform-defined; use `<stdint.h>` (`int32_t`, `int64_t`, `uint64_t`). Signed overflow is undefined behaviour; unsigned overflow wraps modulo 2ⁿ.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; division by zero is undefined behaviour.
- **Strings:** `char` arrays terminated by `'\0'`; `strlen` is O(n); Use explicit destination capacities and check truncation/results. `strncpy` does not guarantee a terminating null byte when the source length reaches the count; it is not a generally safe drop-in replacement for `strcpy`.
- **Equality:** `==` compares scalars and pointer addresses; compare strings with `strcmp` and memory with `memcmp`; structs cannot be compared with `==`.
- **Functions and recursion:** function pointers enable callbacks (`qsort` comparators); no closures. Recursion depth is limited only by stack size; no guaranteed tail-call optimisation.
- **Error handling:** return codes, `errno`, and `NULL` pointers; no exceptions.
- **Iteration idioms:** index loops `for (size_t i = 0; i < n; i++)`, pointer walking `for (int *p = a; p < a + n; p++)`.
- **DSA pitfalls:** check allocation failure and define ownership so allocated storage is eventually freed once; large local arrays overflow the stack (allocate statically or on the heap); `qsort` comparators should return `(a > b) - (a < b)`, not `a - b`; test with `-fsanitize=address,undefined`.

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/strncpy-strncpy-l-wcsncpy-wcsncpy-l-mbsncpy-mbsncpy-l
