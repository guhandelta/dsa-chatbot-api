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
- **Execution and memory:** JIT-compiled (V8, SpiderMonkey); single-threaded event loop; generational garbage collector. Objects and arrays are passed by reference.
- **Integers and overflow:** `number` is an IEEE-754 double; integers are exact only up to 2⁵³−1 (`Number.MAX_SAFE_INTEGER`). `BigInt` (`10n`) is arbitrary precision and cannot mix with `number` in arithmetic. Bitwise operators truncate to 32-bit signed integers.
- **Division and modulo:** `/` is always floating point; integer division is `Math.trunc(a / b)` or `Math.floor(a / b)`; `%` takes the sign of the dividend (`-7 % 3 === -1`).
- **Strings:** immutable, UTF-16 code units; `s.length` counts units, not characters; `[...s]` iterates code points.
- **Equality:** `===` compares without coercion (use it); `==` coerces (`"0" == 0` is true). Objects compare by reference. `NaN !== NaN`; use `Number.isNaN`.
- **Functions and recursion:** first-class functions, closures, arrow functions, generators. No tail-call optimisation in V8; stack depth is roughly 10,000 frames.
- **Error handling:** `try` / `catch` / `finally`; `throw new Error(...)`; async errors via rejected promises.
- **Iteration idioms:** `for...of` (values), `for...in` (keys, avoid on arrays), `map` / `filter` / `reduce`, destructuring (`[a, b] = [b, a]`), spread.
- **DSA pitfalls:** `arr.sort()` with no comparator sorts as strings; `Array.shift()` is O(n); `new Array(n).fill([])` shares one inner array (use `Array.from({ length: n }, () => [])`); plain objects coerce keys to strings, so prefer `Map` and `Set`.
