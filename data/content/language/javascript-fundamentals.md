---
track: language
difficulty: Easy
language: javascript
category: Fundamentals
source: authored
io_mode: function
---
# JavaScript fundamentals — Easy — Fundamentals

- **Paradigm and typing:** multi-paradigm, prototype-based objects with `class` syntax; dynamic, weak typing with implicit coercion. TypeScript adds static types at compile time only.
- **Execution and memory:** Execution and garbage-collection details depend on the engine and host. Function arguments are passed by value; an object value refers to a shared object, so mutation can be visible to the caller while reassigning the parameter cannot reassign the caller's variable.
- **Integers and overflow:** `number` is an IEEE-754 double; integers are exact only up to 2⁵³−1 (`Number.MAX_SAFE_INTEGER`). `BigInt` (`10n`) is arbitrary precision and cannot mix with `number` in arithmetic. Number bitwise operations use 32-bit integers; unsigned right shift (>>>) returns an unsigned result. BigInt supports its own bitwise operations, but not >>>.
- **Division and modulo:** `number` division uses floating-point arithmetic; `bigint` division truncates toward zero; integer division is `Math.trunc(a / b)` or `Math.floor(a / b)`; `%` takes the sign of the dividend (`-7 % 3 === -1`).
- **Strings:** immutable, UTF-16 code units; `s.length` counts units, not characters; `[...s]` iterates code points.
- **Equality:** `===` compares without coercion (use it); `==` coerces (`"0" == 0` is true). Objects compare by reference. `NaN !== NaN`; use `Number.isNaN`.
- **Functions and recursion:** first-class functions, closures, arrow functions, generators. Available recursion depth depends on the engine, stack configuration and function frame size; no portable fixed frame count is guaranteed.
- **Error handling:** `try` / `catch` / `finally`; `throw new Error(...)`; async errors via rejected promises.
- **Iteration idioms:** `for...of` (values), `for...in` (keys, avoid on arrays), `map` / `filter` / `reduce`, destructuring (`[a, b] = [b, a]`), spread.
- **DSA pitfalls:** `arr.sort()` with no comparator sorts as strings; `Array.shift()` is O(n); `new Array(n).fill([])` shares one inner array (use `Array.from({ length: n }, () => [])`); plain objects coerce keys to strings, so prefer `Map` and `Set`.

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors/Too_much_recursion
