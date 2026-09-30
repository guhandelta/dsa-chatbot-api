---
track: language
difficulty: Easy
language: typescript
category: Fundamentals
source: authored
io_mode: function
---
# TypeScript fundamentals — Easy — Fundamentals

- **Paradigm and typing:** typed superset of JavaScript; static, structural typing (compatibility by shape, not by name) with generics, union and intersection types, literal types, tuples and control-flow narrowing. `strict` mode enables `strictNullChecks`, `noImplicitAny` and related checks.
- **Execution and memory:** types are erased at compile time; `tsc` (or type stripping in Node 23.6+, Deno, Bun) emits plain JavaScript, so runtime behaviour, garbage collection and performance are identical to JavaScript.
- **Integers and overflow:** `number` (IEEE-754 double) and `bigint` types, with the same limits as JavaScript; the type system cannot distinguish integers from floats.
- **Division and modulo:** identical to JavaScript: `/` is floating point, `Math.trunc(a / b)` for integer division, `%` takes the sign of the dividend.
- **Strings:** `string` type (UTF-16 at runtime); template literal types such as `` `${number},${number}` `` describe string patterns at compile time.
- **Equality:** runtime equality is JavaScript's (`===`, objects by reference). Type compatibility is structural: two types with the same shape are interchangeable.
- **Functions and recursion:** typed signatures, optional and default parameters, overloads, generic functions `<T>(x: T) => T`, arrow functions. Stack depth is the host engine's (roughly 10,000 frames in V8).
- **Error handling:** `try` / `catch` / `finally`; under `strict`, the `catch` variable is `unknown` and must be narrowed (`if (e instanceof Error)`).
- **Iteration idioms:** `for...of`, typed tuples (`[number, number]`), `readonly` arrays, `as const`, the `satisfies` operator, destructuring with types.
- **DSA pitfalls:** types do not exist at runtime, so `as` casts and the non-null `!` operator silence errors without checking; `arr[i]` is typed `T` rather than `T | undefined` unless `noUncheckedIndexedAccess` is on; `Map.get` returns `V | undefined`; numeric `enum`s compile to runtime objects with reverse mappings (prefer union literal types); every JavaScript pitfall (string-based default sort, O(n) `shift`, shared `fill([])` rows) still applies.
