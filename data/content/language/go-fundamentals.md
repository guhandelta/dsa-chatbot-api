---
track: language
difficulty: Easy
language: go
category: Fundamentals
source: authored
io_mode: function
---
# Go fundamentals — Easy — Fundamentals

- **Paradigm and typing:** imperative with composition instead of inheritance (struct embedding) and implicitly satisfied interfaces; static, strong typing with local inference (`x := 5`); generics with type parameters and constraints (`[T cmp.Ordered]`). No implicit numeric conversions.
- **Execution and memory:** compiled to native code; concurrent garbage collector; escape analysis decides stack or heap allocation. Assignment copies values, including arrays and structs; slices, maps and channels are small headers that share their underlying data.
- **Integers and overflow:** `int` and `uint` are implementation-specific 32- or 64-bit types; sized types `int8`…`int64`, `uint8`…`uint64`. Overflow wraps silently (defined behaviour, not undefined). `math/big` is arbitrary precision; untyped constants are exact at compile time.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend (`-7 % 3 == -1`); For a positive divisor `b`, compute `r := a % b` and add `b` only when `r < 0`, avoiding an unnecessary potentially overflowing addition.
- **Strings:** immutable byte sequences, conventionally UTF-8; `s[i]` is a byte; `for i, r := range s` yields runes (code points); `[]byte(s)` and `[]rune(s)` copy; build with `strings.Builder`.
- **Equality:** `==` works on comparable types (numbers, strings, booleans, pointers, channels, arrays, and structs of comparable fields); slices, maps and functions compare only with `nil`, so use `slices.Equal`, `maps.Equal` or `reflect.DeepEqual`.
- **Functions and recursion:** first-class functions, closures, multiple return values, variadic parameters, `defer`. Goroutine stacks can grow, but remain subject to runtime and resource limits; unbounded recursion can still fail. Do not depend on a fixed recursion depth or on tail-call elimination. A recursive closure must be declared first: `var dfs func(int) int; dfs = func(u int) int { ... }`.
- **Error handling:** errors are returned values (`v, err := f(); if err != nil { ... }`); `panic` and `recover` are reserved for unrecoverable bugs.
- **Iteration idioms:** `for i, v := range slice`, `for k, v := range m`, `for i := range n` (Go 1.22+), range-over-function iterators (Go 1.23+), built-in `min`, `max`, `clear`, and the `slices` and `maps` packages.
- **DSA pitfalls:** `append` may write into a shared backing array, so two slices cut from one base can overwrite each other (copy, or use a full slice expression `a[lo:hi:hi]`); a 2D grid needs `make` for every row; reading a missing map key returns the zero value (use `v, ok := m[k]`); writing to a nil map panics; `for _, v := range structs` copies each element; map iteration order is randomised.

Correction sources reviewed October 17, 2026 (scope: the qualifications above):

- https://go.dev/ref/spec
- https://pkg.go.dev/runtime/debug#SetMaxStack
