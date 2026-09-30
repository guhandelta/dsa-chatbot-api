# DSA Knowledge Base: Ten-Language Reference

## Knowledge base conventions

Every `###` heading is one self-contained retrieval chunk, and every `####` heading is one code chunk for a single language; a code chunk that reuses a helper class names the chunk that defines it.

### Chunking and metadata schema

Meta: category=reference | topic=kb-conventions | languages=all | tags=rag, chunking, metadata

- **Split rule:** split on `##`, `###` and `####`. Carry the parent `##` and `###` titles into each child chunk's metadata.
- **`###` chunks** start with one `Meta:` line of `key=value` pairs separated by `|`. Keys: `category` (language-fundamentals, language-library, data-structure, algorithm, paradigm, reference), `topic` (kebab-case slug), `languages` (`all` or a list), `tags`, and `time` / `space` where a complexity applies.
- **`####` code chunks** are titled `<Topic> — <Language>` (or `— all languages` for one side-by-side block), so topic and language are parsed from the heading. Each holds one code block with its language tag, plus at most one line of notes.
- **Language slugs:** python, javascript, typescript, java, csharp, c, cpp, go, rust, ruby.
- **Complexity notation:** n = elements, V = vertices, E = edges, k = key or pattern length. "Amortised" = averaged over a sequence of operations.
- **Language baselines:** Python 3.12, JavaScript ES2023 (Node 20+), TypeScript 5.x in `strict` mode, Java 21, C# 12 (.NET 8), C17, C++20, Go 1.24, Rust 2021 edition, Ruby 3.3.
- **Anchor algorithms** with code in all ten languages: binary heap, union-find, merge sort, quicksort, binary search, BFS, Dijkstra. Other topics use a Python reference implementation, plus other languages where the standard library lacks the structure or the idiom differs.

## Language fundamentals

Each language chunk uses the same fields in the same order, so a query about one property (overflow, equality, recursion depth) retrieves a comparable answer for any language.

### Python fundamentals

Meta: category=language-fundamentals | topic=python-fundamentals | languages=python | tags=typing, memory, integers, strings, recursion, pitfalls

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

### JavaScript fundamentals

Meta: category=language-fundamentals | topic=javascript-fundamentals | languages=javascript | tags=typing, memory, numbers, strings, recursion, pitfalls

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

### TypeScript fundamentals

Meta: category=language-fundamentals | topic=typescript-fundamentals | languages=typescript | tags=typing, generics, type-erasure, strict-mode, narrowing, pitfalls

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

### Java fundamentals

Meta: category=language-fundamentals | topic=java-fundamentals | languages=java | tags=typing, memory, integers, strings, generics, pitfalls

- **Paradigm and typing:** class-based object-oriented with functional features (lambdas, streams, records, sealed types); static, strong typing; generics are type-erased at runtime.
- **Execution and memory:** compiles to JVM bytecode, JIT-compiled at runtime; garbage collected (G1 by default). Primitives (`int`, `long`, `double`, `char`, `boolean`) live by value; everything else is a reference.
- **Integers and overflow:** `int` is 32-bit, `long` 64-bit, both signed two's complement; overflow wraps silently. `Math.addExact` throws on overflow; `BigInteger` is arbitrary precision.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; `Math.floorMod(a, b)` gives a non-negative result for positive b.
- **Strings:** immutable `String` (UTF-16); `charAt(i)` is O(1); build with `StringBuilder`; `s.toCharArray()` for in-place work.
- **Equality:** `==` compares primitives by value and objects by reference; use `.equals` for objects. `Integer` values outside −128..127 are distinct objects, so `==` on boxed integers is a common bug.
- **Functions and recursion:** methods live in classes; lambdas implement functional interfaces (`Function`, `Comparator`). Default thread stack is about 512 KB–1 MB (roughly 10,000–20,000 frames); run deep recursion in a `Thread` with a larger stack size.
- **Error handling:** checked and unchecked exceptions; `try` / `catch` / `finally`, try-with-resources.
- **Iteration idioms:** enhanced `for (int x : arr)`, `IntStream.range`, streams (`list.stream().filter(...).toList()`), `var` for local type inference.
- **DSA pitfalls:** comparator by subtraction (`(a, b) -> a - b`) overflows, so use `Integer.compare`; boxing in `List<Integer>` costs memory and speed; avoid legacy `Stack`, `Vector` and `Hashtable`.

### C# fundamentals

Meta: category=language-fundamentals | topic=csharp-fundamentals | languages=csharp | tags=typing, memory, integers, strings, generics, pitfalls

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

### C fundamentals

Meta: category=language-fundamentals | topic=c-fundamentals | languages=c | tags=typing, memory, pointers, integers, strings, pitfalls

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

### C++ fundamentals

Meta: category=language-fundamentals | topic=cpp-fundamentals | languages=cpp | tags=typing, memory, raii, templates, integers, pitfalls

- **Paradigm and typing:** multi-paradigm (procedural, object-oriented, generic, functional); static typing with implicit numeric conversions; templates and C++20 concepts provide compile-time generics.
- **Execution and memory:** compiled to native code; value semantics by default; RAII ties resource lifetime to scope. Smart pointers (`std::unique_ptr`, `std::shared_ptr`) replace manual `new` / `delete`; move semantics avoid copies.
- **Integers and overflow:** same as C: use `int64_t` / `long long` for large values; signed overflow is undefined behaviour; unsigned wraps.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend.
- **Strings:** mutable `std::string` of bytes; `std::string_view` for non-owning slices; `+=` with `reserve` for building.
- **Equality:** `==` compares values for standard types; custom types define `operator==`, or `= default` the C++20 `operator<=>` for all comparisons.
- **Functions and recursion:** free functions, member functions, lambdas with captures (`[&]`, `[=]`), `std::function`. Recursion depth limited by stack size; recursive lambdas need `std::function` or C++23 deducing `this`.
- **Error handling:** exceptions (`throw`, `try`, `catch`), `std::optional` and `std::expected` (C++23) for recoverable failures.
- **Iteration idioms:** range-for `for (auto& x : v)`, structured bindings `auto [k, v] = pair`, `<algorithm>` and C++20 ranges (`std::ranges::sort(v)`).
- **DSA pitfalls:** `map[key]` inserts a default when missing (use `find` or `contains`); `vector` growth invalidates iterators, pointers and references; `v.size() - 1` wraps when empty because `size()` is unsigned; comparators must be strict weak orderings (`<`, not `<=`); `unordered_map` with default hashing can be attacked by crafted keys.

### Go fundamentals

Meta: category=language-fundamentals | topic=go-fundamentals | languages=go | tags=typing, memory, slices, integers, strings, errors, generics, pitfalls

- **Paradigm and typing:** imperative with composition instead of inheritance (struct embedding) and implicitly satisfied interfaces; static, strong typing with local inference (`x := 5`); generics with type parameters and constraints (`[T cmp.Ordered]`). No implicit numeric conversions.
- **Execution and memory:** compiled to native code; concurrent garbage collector; escape analysis decides stack or heap allocation. Assignment copies values, including arrays and structs; slices, maps and channels are small headers that share their underlying data.
- **Integers and overflow:** `int` and `uint` are 64-bit on 64-bit platforms; sized types `int8`…`int64`, `uint8`…`uint64`. Overflow wraps silently (defined behaviour, not undefined). `math/big` is arbitrary precision; untyped constants are exact at compile time.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend (`-7 % 3 == -1`); use `((a % b) + b) % b` for a non-negative result.
- **Strings:** immutable byte sequences, conventionally UTF-8; `s[i]` is a byte; `for i, r := range s` yields runes (code points); `[]byte(s)` and `[]rune(s)` copy; build with `strings.Builder`.
- **Equality:** `==` works on comparable types (numbers, strings, booleans, pointers, channels, arrays, and structs of comparable fields); slices, maps and functions compare only with `nil`, so use `slices.Equal`, `maps.Equal` or `reflect.DeepEqual`.
- **Functions and recursion:** first-class functions, closures, multiple return values, variadic parameters, `defer`. Goroutine stacks start small and grow on demand up to 1 GB on 64-bit systems, so deep recursion rarely overflows; there is no tail-call optimisation. A recursive closure must be declared first: `var dfs func(int) int; dfs = func(u int) int { ... }`.
- **Error handling:** errors are returned values (`v, err := f(); if err != nil { ... }`); `panic` and `recover` are reserved for unrecoverable bugs.
- **Iteration idioms:** `for i, v := range slice`, `for k, v := range m`, `for i := range n` (Go 1.22+), range-over-function iterators (Go 1.23+), built-in `min`, `max`, `clear`, and the `slices` and `maps` packages.
- **DSA pitfalls:** `append` may write into a shared backing array, so two slices cut from one base can overwrite each other (copy, or use a full slice expression `a[lo:hi:hi]`); a 2D grid needs `make` for every row; reading a missing map key returns the zero value (use `v, ok := m[k]`); writing to a nil map panics; `for _, v := range structs` copies each element; map iteration order is randomised.

### Rust fundamentals

Meta: category=language-fundamentals | topic=rust-fundamentals | languages=rust | tags=typing, ownership, borrowing, integers, strings, pitfalls

- **Paradigm and typing:** multi-paradigm with traits instead of inheritance; static, strong typing with inference; generics are monomorphised; `Option<T>` replaces null.
- **Execution and memory:** compiled to native code; no garbage collector. Ownership rules: each value has one owner, dropped when the owner leaves scope; borrowing allows many `&T` or one `&mut T` at a time, checked at compile time. `Box<T>` for heap allocation, `Rc<RefCell<T>>` for shared mutable ownership.
- **Integers and overflow:** explicit widths (`i32`, `i64`, `u64`, `usize` for indices); overflow panics in debug builds and wraps in release. Use `checked_add`, `wrapping_add`, `saturating_add` to choose. No implicit numeric conversions; cast with `as`.
- **Division and modulo:** integer `/` truncates toward zero; `%` takes the sign of the dividend; `rem_euclid` gives a non-negative result.
- **Strings:** `String` (owned) and `&str` (borrowed), always valid UTF-8; `s[i]` is not allowed, so use `s.as_bytes()[i]` for ASCII or `s.chars()` for characters.
- **Equality:** `==` via the `PartialEq` trait; `#[derive(PartialEq, Eq, Hash, PartialOrd, Ord)]` generates comparisons. `f64` is only `PartialOrd`, so floats need `total_cmp` to sort.
- **Functions and recursion:** closures (`|x| x + 1`) implement `Fn`, `FnMut` or `FnOnce`; iterators are lazy and zero-cost. Main thread stack is 8 MB on Linux; spawned threads default to 2 MB (set with `std::thread::Builder::stack_size`).
- **Error handling:** `Result<T, E>` with the `?` operator; `panic!` for unrecoverable bugs.
- **Iteration idioms:** `for x in &v`, `iter().enumerate()`, `zip`, `map` / `filter` / `collect`, `windows(k)`, `chunks(k)`, `rev()`.
- **DSA pitfalls:** two mutable references into one `Vec` are rejected, so use indices or `split_at_mut`; subtracting below zero on `usize` panics; `HashMap` iteration order is random per run (use `BTreeMap` for deterministic output); trees and graphs with back-pointers are easiest as index-based arenas (`Vec<Node>` with `usize` ids).

### Ruby fundamentals

Meta: category=language-fundamentals | topic=ruby-fundamentals | languages=ruby | tags=typing, memory, integers, strings, blocks, pitfalls

- **Paradigm and typing:** pure object-oriented (every value is an object, including integers and `nil`) with functional blocks; dynamic, strong typing with duck typing; optional RBS type signatures.
- **Execution and memory:** interpreted by CRuby's YARV virtual machine, with the optional YJIT compiler; generational, incremental garbage collector. Variables hold references.
- **Integers and overflow:** `Integer` is arbitrary precision and never overflows; `Float` is IEEE-754 double; `Rational` for exact fractions.
- **Division and modulo:** integer `/` floors toward negative infinity (`-7 / 2 == -4`); `%` takes the sign of the divisor (`-7 % 3 == 2`); `fdiv` returns a float.
- **Strings:** mutable `String` (UTF-8 by default); `<<` appends in place, while `+` allocates a new string; `freeze` makes a string immutable; symbols (`:name`) are immutable interned identifiers, ideal as hash keys.
- **Equality:** `==` compares values; `equal?` compares identity; `eql?` is used by `Hash` (so `1.eql?(1.0)` is false); `<=>` is the three-way comparison used by sorting.
- **Functions and recursion:** methods, blocks (`{ |x| ... }`), procs and lambdas; `yield` calls the block. Default recursion depth is roughly 10,000 frames (`SystemStackError` beyond); tail-call optimisation is off by default.
- **Error handling:** `begin` / `rescue` / `ensure`; `raise ArgumentError, "msg"`.
- **Iteration idioms:** `each`, `each_with_index`, `map`, `select`, `reduce` / `inject`, `times`, `upto`, `each_cons(k)` for sliding windows, `each_slice(k)` for chunks, parallel assignment (`a, b = b, a`).
- **DSA pitfalls:** `Array.new(n, [])` shares one inner array (use `Array.new(n) { [] }`); `Hash.new([])` shares one default array (use `Hash.new { |h, k| h[k] = [] }`); `array.shift` is O(1) amortised in CRuby but `array.delete_at(0)` in loops is not; `array.include?` is O(n), so use `Set`.

## Language data structures and algorithm APIs

Each chunk lists what one language's standard library provides, with the calls to use and their cost; "Build" means no standard type exists.

### Python data structures and algorithm APIs

Meta: category=language-library | topic=python-library | languages=python | tags=list, dict, set, deque, heapq, bisect, sort

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `list` | `append`/`pop()` O(1) amortised; `insert(0, x)`/`pop(0)` O(n); growth ≈ 1.125× |
| Fixed / typed array | `array.array`, `tuple`, `bytearray` | Compact storage; tuple is immutable and hashable |
| Stack | `list` | `append`, `pop`, peek `s[-1]` |
| Queue / deque | `collections.deque` | `append`/`appendleft`/`pop`/`popleft` O(1); index access O(n) |
| Hash map | `dict` | Get/set/delete O(1) average; insertion-ordered (guaranteed 3.7+); `get(k, default)`, `setdefault` |
| Default map | `collections.defaultdict` | `defaultdict(list)` auto-creates missing values |
| Counter / multiset | `collections.Counter` | Counts in O(n); `most_common(k)` |
| Hash set | `set`, `frozenset` | Add/remove/membership O(1) average; `&`, `\|`, `-` set algebra |
| Priority queue | `heapq` on a `list` | Min-heap; `heappush`/`heappop` O(log n); `heapify` O(n); `nlargest(k, xs)` |
| Sorted list / map | Build, or third-party `sortedcontainers` (`SortedList`, `SortedDict`) | O(log n) insert and lookup in the package |
| Linked list | Build | `deque` covers most use cases |
| Bit set | `int` | Arbitrary-width bitmask |

| Algorithm | API |
| --- | --- |
| Sort | `sorted(xs, key=f, reverse=True)`, `xs.sort()`; Timsort, stable |
| Binary search | `bisect.bisect_left`, `bisect_right`, `insort` |
| Combinatorics | `itertools.permutations`, `combinations`, `product`, `accumulate` |
| Memoisation | `@functools.cache`, `@lru_cache(maxsize=n)` |
| Number theory | `math.gcd`, `math.lcm`, `math.comb`, `pow(b, e, mod)`, `math.isqrt` |
| Bits | `x.bit_count()`, `x.bit_length()` |

### JavaScript data structures and algorithm APIs

Meta: category=language-library | topic=javascript-library | languages=javascript | tags=array, map, set, typed-array, sort

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Array` | `push`/`pop` O(1) amortised; `shift`/`unshift`/`splice` O(n) |
| Typed array | `Int32Array`, `Float64Array`, `Uint8Array` | Fixed-size, contiguous, numeric only; fastest for DP tables |
| Queue / deque | Build | Array with a head index gives O(1) dequeue |
| Hash map | `Map` | `get`/`set`/`has`/`delete` O(1) average; insertion-ordered; any key type, objects by reference |
| Hash set | `Set` | `add`/`has`/`delete` O(1) average; insertion-ordered |
| Weak map / set | `WeakMap`, `WeakSet` | Object keys that do not prevent garbage collection; memo caches |
| Priority queue | Build | Binary heap class |
| Sorted map / set | Build | Balanced tree or sorted array with binary search |
| Linked list | Build | — |
| Big integers | `BigInt` | Arbitrary precision, `123n` literals |

| Algorithm | API |
| --- | --- |
| Sort | `arr.sort(cmp)` in place, `arr.toSorted(cmp)` copy; stable (ES2019+); numeric sort needs `(a, b) => a - b` |
| Binary search | Build |
| Search | `indexOf`, `includes`, `find`, `findIndex`, `findLast` |
| Aggregation | `reduce`, `Object.groupBy` / `Map.groupBy` (ES2024) |
| Bits | `Math.clz32`; popcount must be built |

### TypeScript data structures and algorithm APIs

Meta: category=language-library | topic=typescript-library | languages=typescript | tags=typed-array, map, set, record, tuple, generics, sort

TypeScript runs on the JavaScript standard library, so costs match JavaScript; this chunk lists how each structure is typed and what must be built as a generic class.

| Structure | Type annotation | Key operations and notes |
| --- | --- | --- |
| Dynamic array / stack | `number[]`, `Array<T>`, `readonly T[]` | `push`/`pop` O(1) amortised; `readonly` blocks mutation at compile time |
| Tuple | `[number, number]`, `readonly [row: number, col: number]` | Fixed-length heterogeneous arrays; ideal for heap entries and edges |
| Typed array | `Int32Array`, `Float64Array` | Fixed-size numeric storage for DP tables |
| Queue / deque | Build a generic `Queue<T>` | Array with a head index gives O(1) dequeue |
| Hash map | `Map<K, V>` | O(1) average; `get` returns `V \| undefined`; object keys compare by reference |
| String-keyed record | `Record<string, V>` | Plain object; use only for string keys known at compile time |
| Hash set | `Set<T>` | O(1) average `has`, `add`, `delete` |
| Priority queue | Build a generic `Heap<T>` with a comparator | See the "Binary heap — TypeScript" chunk |
| Sorted map / set | Build | Balanced tree, or a sorted array with binary search |
| Linked list | Build `ListNode<T> { val: T; next: ListNode<T> \| null }` | — |
| Big integers | `bigint` | `123n` literals; cannot mix with `number` |

| Algorithm | API |
| --- | --- |
| Sort | `arr.sort((a, b) => a - b)` in place; `arr.toSorted(cmp)` returns a copy (requires `lib` ES2023); stable |
| Binary search | Build a generic `lowerBound<T>` with a comparator |
| Search | `indexOf`, `includes`, `find` (returns `T \| undefined`), `findIndex`, `findLast` |
| Aggregation | `reduce<U>(fn, init)`, `Object.groupBy` / `Map.groupBy` (requires `lib` ES2024) |
| Type utilities useful in DSA | `Readonly<T>`, `Partial<T>`, `Record<K, V>`, `ReturnType<F>`, `NonNullable<T>` |

### Java data structures and algorithm APIs

Meta: category=language-library | topic=java-library | languages=java | tags=arraylist, hashmap, treemap, arraydeque, priorityqueue, collections

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `ArrayList<T>` | `add`/`get` O(1); `add(0, x)`/`remove(0)` O(n); growth 1.5× |
| Fixed array | `int[]`, `T[]` | Primitive arrays avoid boxing |
| Stack / queue / deque | `ArrayDeque<T>` | `push`/`pop`, `offer`/`poll`, `offerFirst`/`pollLast` O(1); no nulls |
| Linked list | `LinkedList<T>` | O(1) at ends; O(n) indexed access |
| Hash map | `HashMap<K,V>` | O(1) average; chained buckets become red-black trees at 8 entries; load factor 0.75 |
| Insertion / access-ordered map | `LinkedHashMap<K,V>` | Access-order mode plus `removeEldestEntry` gives an LRU cache |
| Hash set | `HashSet<T>` | O(1) average |
| Sorted map / set | `TreeMap`, `TreeSet` (red-black trees) | O(log n); `floorKey`, `ceilingKey`, `headMap`, `subMap`, `firstKey`, `pollFirst` |
| Priority queue | `PriorityQueue<T>` | Min-heap by default; `offer`/`poll` O(log n); `remove(Object)` O(n); max-heap via `Comparator.reverseOrder()` |
| Bit set | `BitSet` | `set`, `get`, `cardinality`, `nextSetBit` |
| Concurrent | `ConcurrentHashMap`, `ConcurrentSkipListMap`, `ConcurrentLinkedQueue` | Thread-safe variants |

| Algorithm | API |
| --- | --- |
| Sort | `Arrays.sort(int[])` dual-pivot quicksort (unstable); `Arrays.sort(T[])` / `Collections.sort` Timsort (stable); `list.sort(Comparator.comparing(P::age).reversed())` |
| Binary search | `Arrays.binarySearch`, `Collections.binarySearch`; returns `-(insertionPoint) - 1` when absent |
| Utilities | `Arrays.fill`, `Arrays.copyOfRange`, `Collections.reverse`, `Collections.swap` |
| Number theory | `BigInteger.gcd`, `BigInteger.modPow`, `Math.floorMod` |
| Bits | `Integer.bitCount`, `numberOfTrailingZeros`, `numberOfLeadingZeros`, `highestOneBit` |

### C# data structures and algorithm APIs

Meta: category=language-library | topic=csharp-library | languages=csharp | tags=list, dictionary, hashset, sortedset, priorityqueue, linq

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `List<T>` | `Add`/indexer O(1); `Insert(0, x)`/`RemoveAt(0)` O(n); growth 2× |
| Fixed array | `T[]`, `T[,]` (rectangular), `T[][]` (jagged) | Jagged arrays are usually faster |
| Stack | `Stack<T>` | `Push`/`Pop`/`Peek` O(1) |
| Queue | `Queue<T>` | `Enqueue`/`Dequeue`/`Peek` O(1); ring buffer |
| Deque | Build, or `LinkedList<T>` | .NET has no array deque |
| Linked list | `LinkedList<T>` (doubly linked) | `AddFirst`/`AddLast`/`Remove(node)` O(1) |
| Hash map | `Dictionary<K,V>` | O(1) average; `TryGetValue`, `TryAdd`, `GetValueOrDefault`; separate chaining in arrays |
| Hash set | `HashSet<T>` | O(1) average; `UnionWith`, `IntersectWith` |
| Sorted map | `SortedDictionary<K,V>` (red-black tree) | O(log n) insert and lookup |
| Sorted array map | `SortedList<K,V>` | O(log n) lookup, O(n) insert; index access |
| Sorted set | `SortedSet<T>` (red-black tree) | O(log n); `Min`, `Max`, `GetViewBetween(lo, hi)` for range queries |
| Priority queue | `PriorityQueue<TElement, TPriority>` (.NET 6+) | Min-heap by priority; `Enqueue`/`Dequeue` O(log n); no decrease-key; max-heap via reversed `Comparer` |
| Bit set | `BitArray` | Fixed-size bit vector |
| Concurrent | `ConcurrentDictionary`, `ConcurrentQueue` | Thread-safe variants |

| Algorithm | API |
| --- | --- |
| Sort | `Array.Sort` / `List<T>.Sort` introsort (unstable); LINQ `OrderBy`/`ThenBy` stable |
| Binary search | `Array.BinarySearch`, `List<T>.BinarySearch`; returns bitwise complement `~insertionPoint` when absent |
| Utilities | `Array.Fill`, `Array.Reverse`, `Span<T>.Sort` |
| Number theory | `BigInteger.GreatestCommonDivisor`, `BigInteger.ModPow` |
| Bits | `System.Numerics.BitOperations.PopCount`, `TrailingZeroCount`, `LeadingZeroCount` |

### C data structures and algorithm APIs

Meta: category=language-library | topic=c-library | languages=c | tags=array, qsort, bsearch, malloc, posix

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Fixed array | `int a[N]`, `malloc(n * sizeof *a)` | O(1) index; size fixed at allocation |
| Dynamic array | Build with `realloc` | Double capacity on growth for O(1) amortised append |
| Stack | Build | Array plus top index |
| Queue / deque | Build | Ring buffer with head, tail and size |
| Linked list | Build | `struct Node { int val; struct Node *next; }` |
| Hash map | Build, or POSIX `hsearch` (one global table) | Custom table with FNV-1a or similar hash |
| Sorted map | Build, or POSIX `tsearch` / `tfind` / `tdelete` | Binary tree, balanced in glibc |
| Priority queue | Build | Array-backed binary heap |
| Bit set | Build | Array of `uint64_t` words |
| Third-party | `stb_ds.h`, `klib`, `uthash` | Header-only generic containers |

| Algorithm | API |
| --- | --- |
| Sort | `qsort(base, n, size, cmp)`; unstable; comparator returns `<0`, `0`, `>0` |
| Binary search | `bsearch(&key, base, n, size, cmp)`; returns a pointer to any match or `NULL`, no insertion point |
| Memory | `memcpy`, `memmove` (overlapping), `memset`, `memcmp` |
| Bits | `__builtin_popcount`, `__builtin_ctz`, `__builtin_clz` (GCC/Clang, undefined for 0); C23 `<stdbit.h>` `stdc_count_ones` |

### C++ data structures and algorithm APIs

Meta: category=language-library | topic=cpp-library | languages=cpp | tags=stl, vector, unordered\_map, map, priority\_queue, algorithm

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array | `std::vector<T>` | `push_back`/`pop_back` O(1) amortised; `insert`/`erase` middle O(n); `reserve` pre-allocates |
| Fixed array | `std::array<T, N>` | Stack-allocated, bounds-checked `at()` |
| Deque | `std::deque<T>` | O(1) at both ends and O(1) indexing; chunked storage |
| Linked list | `std::list<T>`, `std::forward_list<T>` | O(1) insert/erase given an iterator; `splice` moves nodes in O(1) |
| Stack / queue | `std::stack`, `std::queue` | Adaptors over `deque` by default |
| Priority queue | `std::priority_queue<T>` | Max-heap by default; min-heap with `std::greater<T>` as the third template argument |
| Hash map / set | `std::unordered_map`, `std::unordered_set` | O(1) average; separate chaining; `max_load_factor` 1.0 |
| Sorted map / set | `std::map`, `std::set`, `std::multimap`, `std::multiset` (red-black trees) | O(log n); `lower_bound`, `upper_bound`, `equal_range` |
| Bit set | `std::bitset<N>`, `std::vector<bool>` | `count`, `test`, shifts |
| Non-owning views | `std::span<T>`, `std::string_view` | Slices without copies |

| Algorithm | API (`<algorithm>`, `<numeric>`, `<bit>`) |
| --- | --- |
| Sort | `std::sort` (introsort, unstable), `std::stable_sort`, `std::partial_sort`, `std::nth_element` (O(n) average selection) |
| Binary search | `std::lower_bound` (first ≥), `std::upper_bound` (first >), `std::equal_range`, `std::binary_search` |
| Permutations | `std::next_permutation`, `std::prev_permutation` |
| Sequence ops | `std::reverse`, `std::rotate`, `std::unique` (+ `erase`), `std::iota`, `std::accumulate`, `std::partial_sum` |
| Heap ops on a range | `std::make_heap`, `std::push_heap`, `std::pop_heap` |
| Number theory | `std::gcd`, `std::lcm` |
| Bits | `std::popcount`, `std::countr_zero`, `std::countl_zero`, `std::has_single_bit` |

### Go data structures and algorithm APIs

Meta: category=language-library | topic=go-library | languages=go | tags=slice, map, container-heap, container-list, slices-package, sort

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | slice `[]T` | `append` O(1) amortised (growth 2× below 256 elements, tapering toward 1.25×); pop with `s = s[:len(s)-1]`; `slices.Insert` / `slices.Delete` O(n) |
| Fixed array | `[N]T` | Value type: copied on assignment, comparable, usable as a map key |
| Queue | slice with `q = q[1:]` | O(1) dequeue, but the backing array is only released after `append` reallocates; a head index avoids repeated reslicing |
| Deque / linked list | `container/list` (doubly linked, `any` values) | `PushFront`, `PushBack`, `Remove`, `MoveToFront` O(1); needs type assertions |
| Circular list | `container/ring` | Fixed-size ring of `any` values |
| Hash map | `map[K]V` | O(1) average; `v, ok := m[k]`, `delete(m, k)`, `clear(m)`; Swiss tables since Go 1.24; iteration order randomised |
| Hash set | `map[T]struct{}` | Zero-byte values; `_, ok := set[x]` |
| Priority queue | `container/heap` over a type implementing `heap.Interface` | `heap.Init` O(n), `heap.Push` / `heap.Pop` O(log n), `heap.Fix` after changing a priority |
| Sorted map / set | Build, or third-party `github.com/google/btree` | Sorted slice + `slices.BinarySearch` for small sizes |
| Bit set | Build with `[]uint64`, or `math/big.Int` `SetBit` / `Bit` | — |
| Big integers | `math/big` (`big.Int`, `big.Rat`) | Arbitrary precision |
| Concurrent | channels, `sync.Mutex`, `sync.Map` | Goroutine-safe queues and maps |

| Algorithm | API |
| --- | --- |
| Sort | `slices.Sort` (pdqsort, unstable), `slices.SortFunc(s, cmp)`, `slices.SortStableFunc`; older `sort.Slice`, `sort.SliceStable`, `sort.Ints` |
| Binary search | `slices.BinarySearch(s, x)` returns `(insertionIndex, found)`; `sort.Search(n, pred)` returns the first index where `pred` is true |
| Comparison | `cmp.Compare`, `cmp.Less`, `cmp.Or` (chain tie-breakers) |
| Sequence ops | `slices.Reverse`, `slices.Contains`, `slices.Index`, `slices.Max`, `slices.Min`, `slices.Compact`, `slices.Equal`, built-in `copy`, `min`, `max` |
| Number theory | `new(big.Int).GCD`, `new(big.Int).Exp(b, e, m)` for modular power; build `gcd` for plain `int` |
| Bits | `math/bits.OnesCount64`, `TrailingZeros64`, `LeadingZeros64`, `Len64` |

### Rust data structures and algorithm APIs

Meta: category=language-library | topic=rust-library | languages=rust | tags=vec, vecdeque, hashmap, btreemap, binaryheap, slices

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Vec<T>` | `push`/`pop` O(1) amortised (`pop` returns `Option<T>`); `insert`/`remove` middle O(n); `swap_remove` O(1) |
| Fixed array | `[T; N]`, slices `&[T]` | Stack-allocated; slices borrow any contiguous range |
| Queue / deque | `VecDeque<T>` | Ring buffer; `push_back`/`pop_front` O(1) |
| Linked list | `LinkedList<T>` | Rarely the right choice; prefer `Vec` or `VecDeque` |
| Hash map / set | `HashMap<K,V>`, `HashSet<T>` | SwissTable, O(1) average; SipHash-1-3 default (DoS-resistant, slower); `entry(k).or_insert(v)` |
| Sorted map / set | `BTreeMap<K,V>`, `BTreeSet<T>` | B-tree, O(log n); `range(a..b)`, `first_key_value`, `last_key_value`, `pop_first` |
| Priority queue | `BinaryHeap<T>` | Max-heap; min-heap by wrapping items in `std::cmp::Reverse` |
| Shared ownership | `Rc<RefCell<T>>`, `Arc<Mutex<T>>` | Trees with parent links, shared graph nodes |
| Third-party | `indexmap`, `rustc-hash` (FxHash), `ahash`, `bitvec`, `lru` | Ordered maps, fast hashing, bit sets |

| Algorithm | API (slice methods) |
| --- | --- |
| Sort | `sort`, `sort_by_key` (stable); `sort_unstable`, `sort_unstable_by` (faster); floats via `sort_by(\|a, b\| a.total_cmp(b))` |
| Binary search | `binary_search` returns `Ok(index)` or `Err(insertion_point)`; `partition_point(pred)` for lower bound |
| Selection | `select_nth_unstable(k)` O(n) average |
| Sequence ops | `reverse`, `rotate_left`, `dedup`, `retain`, `windows(k)`, `chunks(k)`, `concat`, `iter().rev()` |
| Bits | `count_ones`, `trailing_zeros`, `leading_zeros`, `is_power_of_two` |
| Number theory | Build `gcd`, or crate `num` |

### Ruby data structures and algorithm APIs

Meta: category=language-library | topic=ruby-library | languages=ruby | tags=array, hash, set, enumerable, bsearch

| Structure | Type | Key operations and cost |
| --- | --- | --- |
| Dynamic array / stack | `Array` | `push`/`<<`/`pop` O(1) amortised; `insert(0, x)` O(n); negative indexing `a[-1]` |
| Queue / deque | `Array` | `shift` and `unshift` are O(1) amortised in CRuby (shared-array optimisation), so an Array works as a deque; `Thread::Queue` for threads |
| Hash map | `Hash` | O(1) average; open addressing; insertion-ordered; `Hash.new(0)` for counters; `fetch(k, default)`, `dig`, `group_by`, `tally` |
| Hash set | `Set` | O(1) average membership; autoloaded since Ruby 3.2 (`require "set"` before) |
| Priority queue | Build | Binary heap class |
| Sorted map / set | Build, or gems `rbtree`, `algorithms` | Sorted `Array` + `bsearch_index` for small sizes |
| Linked list | Build | — |
| Records | `Struct`, `Data.define` (3.2+) | Lightweight node and point types |
| Big integers | `Integer` | Arbitrary precision built in |

| Algorithm | API |
| --- | --- |
| Sort | `sort`, `sort!`, `sort_by { \|x\| -x.age }`, `min_by`, `max_by`, `max(k)`; quicksort-based, not stable (stabilise with `sort_by.with_index { \|x, i\| [key(x), i] }`) |
| Binary search | `bsearch { \|x\| x >= target }` (find-minimum mode), `bsearch_index` |
| Combinatorics | `permutation(k)`, `combination(k)`, `product`, `repeated_combination` |
| Enumerable | `each_cons(k)` sliding window, `each_slice(k)`, `each_with_object`, `inject(:+)`, `sum`, `tally`, `partition`, `chunk_while` |
| Number theory | `Integer#gcd`, `lcm`, `pow(e, mod)`, `Integer.sqrt`, `Prime` library (gem since 3.1) |
| Bits | `x.bit_length`, `x[i]` reads bit i, `x.to_s(2).count("1")` for popcount |

## Data structures

Each chunk defines one structure, its operation costs, when to choose it, and a reference implementation.

### Data structure classification

Meta: category=reference | topic=data-structure-classification | languages=all | tags=linear, non-linear, key-value, specialised, taxonomy, patterns

Linear structures hold elements in a sequence where each has at most one predecessor and one successor. Non-linear structures arrange elements hierarchically (trees, heaps) or as networks (graphs). Key-value and specialised structures are built around one access pattern, such as constant-time lookup, prefix search, set merging or range queries.

| Class | Structure | Common patterns | Chunk topic |
| --- | --- | --- | --- |
| Linear | Array, dynamic array | Two pointers, sliding window, prefix sums, binary search | dynamic-array, two-pointers, sliding-window, prefix-sums |
| Linear | String | Anagrams, palindromes, substring windows, pattern matching | string, string-matching |
| Linear | Linked list (singly, doubly, circular) | Fast and slow pointers, in-place reversal, merging | linked-list |
| Linear | Stack | Bracket matching, monotonic stack, backtracking, iterative DFS | stack, monotonic-stack |
| Linear | Queue (standard, deque, circular) | BFS, level-order traversal, sliding-window maximum | queue-deque, bfs |
| Non-linear | Binary tree | Pre-, in-, post- and level-order traversal, lowest common ancestor | tree-traversal, lowest-common-ancestor |
| Non-linear | Binary search tree, self-balancing trees (AVL, red-black, B-tree) | Ordered queries (floor, ceiling, range), validation | binary-search-tree, balanced-bst |
| Non-linear | Heap / priority queue | Top K, merge K sorted lists, two heaps | binary-heap, heap-patterns |
| Non-linear | Graph (directed, undirected, weighted, unweighted) | DFS, BFS, shortest paths, topological sort, MST | graph-representation, graph-algorithm-selection |
| Key-value | Hash table, hash map, hash set | Frequency counting, duplicate checks, subarray sum equals K | hash-table, hashing-patterns |
| Specialised | Trie | Autocomplete, spell checking, prefix matching | trie |
| Specialised | Disjoint set union (union-find) | Cycle detection in undirected graphs, Kruskal's MST, connected components | union-find, minimum-spanning-tree |
| Specialised | Segment tree, Fenwick tree | Range sum, min or max queries with updates | segment-tree, fenwick-tree |
| Specialised | LRU cache, Bloom filter, skip list | Eviction, approximate membership, concurrent ordered sets | lru-cache, bloom-filter, skip-list |

### Array and dynamic array

Meta: category=data-structure | topic=dynamic-array | languages=all | tags=array, vector, amortised, contiguous | time=O(1) index, O(1) amortised append, O(n) middle insert | space=O(n)

An array stores elements of one type contiguously, so index access is O(1) and iteration is cache-friendly. A dynamic array keeps spare capacity; when full it allocates 1.5–2× more and copies, which makes append O(1) amortised. Inserting or deleting in the middle shifts every later element, costing O(n). Choose it by default for ordered collections accessed by index. Common patterns: two pointers, sliding window, prefix sums, and binary search on sorted arrays.

#### Dynamic array — C

```c
#include <stdlib.h>

typedef struct { int *data; size_t len, cap; } IntVec;

int vec_push(IntVec *v, int x) {
    if (v->len == v->cap) {
        size_t ncap = v->cap ? v->cap * 2 : 8;
        int *p = realloc(v->data, ncap * sizeof *p);
        if (!p) return -1;            /* old buffer is still valid on failure */
        v->data = p; v->cap = ncap;
    }
    v->data[v->len++] = x;
    return 0;
}

void vec_free(IntVec *v) { free(v->data); v->data = NULL; v->len = v->cap = 0; }
```

### String

Meta: category=data-structure | topic=string | languages=all | tags=string, anagram, palindrome, substring, character-count, expand-around-center, immutability | time=O(n) for most scans, O(k) to copy a substring of length k | space=O(n)

A string is a sequence of characters stored as an array of code units, so indexing and scanning behave like an array. Strings are immutable in Python, JavaScript, TypeScript, Java, C#, Go and Rust's `&str`, so every modification creates a new string; collect pieces in a list or builder and join once, which is O(n) overall instead of O(n²). Taking a substring copies it in most languages, but is a zero-copy view in Go, Rust (`&s[a..b]`) and C++ (`std::string_view`). For lowercase letters, map a character to an index with `c - 'a'` (C, C++, Java, C#, Go), `ord(c) - ord('a')` (Python), `c.charCodeAt(0) - 97` (JavaScript, TypeScript), `c as u8 - b'a'` (Rust) or `c.ord - 97` (Ruby), then count in a 26-slot array.

| Problem family | Technique | Example problems |
| --- | --- | --- |
| Anagrams | 26-slot count array or sorted-string key; fixed-size sliding window for "all anagrams in s" | Valid anagram, group anagrams, find all anagrams in a string, permutation in string |
| Palindromes | Two pointers from both ends; expand around each of the 2n−1 centres in O(n²); Manacher in O(n) | Valid palindrome, longest palindromic substring, count palindromic substrings |
| Substring windows | Variable sliding window with a character-count map | Longest substring without repeating characters, minimum window substring |
| Subsequences | Two pointers, or DP over two strings | Is subsequence, longest common subsequence, edit distance |
| Parsing | Stack or index scanning | Decode string, basic calculator, valid parentheses |
| Pattern search | KMP, Z-algorithm, Rabin–Karp | Find the first occurrence, repeated substring pattern |

#### Anagram and palindrome checks — Python

```python
from collections import Counter

def is_anagram(s, t):
    return len(s) == len(t) and Counter(s) == Counter(t)

def find_anagrams(s, p):                    # start indices of p's anagrams in s
    need, window, res, k = Counter(p), Counter(), [], len(p)
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= k:
            left = s[i - k]
            window[left] -= 1
            if window[left] == 0:
                del window[left]
        if window == need:
            res.append(i - k + 1)
    return res

def is_palindrome(s):                       # letters and digits only, case-insensitive
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i += 1; j -= 1
    return True

def longest_palindrome(s):                  # expand around each centre, O(n²)
    best_lo, best_hi = 0, 0
    for c in range(len(s)):
        for lo, hi in ((c, c), (c, c + 1)):   # odd and even centres
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1; hi += 1
            if hi - lo - 1 > best_hi - best_lo:
                best_lo, best_hi = lo + 1, hi
    return s[best_lo:best_hi]
```

### Linked list

Meta: category=data-structure | topic=linked-list | languages=all | tags=singly-linked, doubly-linked, circular-linked, fast-slow-pointers, floyd-cycle, reversal, sentinel | time=O(1) insert at head or given node, O(n) search and index | space=O(n)

A linked list chains nodes by pointers instead of storing them contiguously. Access by position is O(n) and pointer chasing has poor cache locality, so prefer a dynamic array unless you splice nodes you already hold.

| Variant | Links per node | Strength | Typical use |
| --- | --- | --- | --- |
| Singly linked | `next` | O(1) insert and delete at the head | Stacks, adjacency lists, hash chains |
| Doubly linked | `next`, `prev` | O(1) removal of a known node, traversal both ways | LRU caches, deques, browser history |
| Circular | tail's `next` points to the head (singly or doubly) | Any node reaches every node; no null end | Round-robin scheduling, Josephus problem, ring buffers |

When traversing a circular list, stop on returning to the start node rather than on `null`. A dummy (sentinel) head node removes special cases when the head itself may change. Common patterns: fast and slow pointers (Floyd's cycle detection and cycle entry point, middle node, k-th node from the end via a k-step lead), in-place reversal (whole list, sublist, groups of k), and merging sorted lists.

#### Linked list reversal, fast and slow pointers, merge — Python

```python
class Node:
    __slots__ = ("val", "next")
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt

def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def middle(head):                        # second middle when the length is even
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

def cycle_start(head):                   # entry node of a cycle, or None (Floyd)
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:                 # met inside the cycle
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None                          # has_cycle(head) == (cycle_start(head) is not None)

def merge_sorted(a, b):
    dummy = tail = Node(0)               # sentinel avoids a special case for the head
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
```

#### Linked list reverse — Rust

```rust
struct Node { val: i32, next: Option<Box<Node>> }

fn reverse(mut head: Option<Box<Node>>) -> Option<Box<Node>> {
    let mut prev = None;
    while let Some(mut node) = head {
        head = node.next.take();
        node.next = prev;
        prev = Some(node);
    }
    prev
}
```

Rust singly linked lists use `Option<Box<Node>>`; doubly linked lists need `Rc<RefCell<Node>>` with `Weak` back-pointers, or an index-based arena.

### Stack

Meta: category=data-structure | topic=stack | languages=all | tags=lifo, push, pop, dfs, parentheses | time=O(1) push, pop, peek | space=O(n)

A stack is last-in, first-out: `push`, `pop` and `peek` are all O(1). It is backed by a dynamic array (push and pop at the end). Common patterns: bracket matching (valid parentheses), monotonic stacks for next-greater-element problems, backtracking state, depth-first search without recursion, expression evaluation (postfix, shunting-yard) and undo history.

#### Balanced brackets — Python

```python
def is_balanced(s):
    pairs, st = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{":
            st.append(ch)
        elif ch in pairs:
            if not st or st.pop() != pairs[ch]:
                return False
    return not st
```

### Queue, deque and circular queue

Meta: category=data-structure | topic=queue-deque | languages=all | tags=fifo, deque, double-ended, circular-queue, ring-buffer, bfs, level-order | time=O(1) enqueue, dequeue, both ends for deque | space=O(n)

A queue is first-in, first-out. Variants: the standard queue; the double-ended queue (deque), which allows O(1) insert and remove at both ends; and the circular queue, a fixed-capacity ring buffer whose head and tail indices wrap around with modulo so no element is ever shifted. Library queues and deques are ring buffers or linked lists underneath. Common patterns: breadth-first search, level-order tree traversal, task scheduling, sliding-window maximum and 0-1 BFS. Removing from the front of a plain dynamic array is O(n) in most languages (Go reslicing and CRuby's `shift` are O(1) exceptions), so use a real queue type.

#### Queue with head index — JavaScript

```javascript
class Queue {
  #items = []; #head = 0;
  push(x) { this.#items.push(x); }
  shift() {
    const x = this.#items[this.#head++];
    if (this.#head > 1024 && this.#head * 2 > this.#items.length) {
      this.#items = this.#items.slice(this.#head); this.#head = 0;
    }
    return x;
  }
  get size() { return this.#items.length - this.#head; }
}
```

#### Circular queue (ring buffer) — C

```c
#define CAP 1024
typedef struct { int buf[CAP]; int head, tail, size; } Queue;

int q_push(Queue *q, int x) {
    if (q->size == CAP) return -1;
    q->buf[q->tail] = x; q->tail = (q->tail + 1) % CAP; q->size++;
    return 0;
}

int q_pop(Queue *q, int *out) {
    if (!q->size) return -1;
    *out = q->buf[q->head]; q->head = (q->head + 1) % CAP; q->size--;
    return 0;
}
```

#### Deque — C#

```csharp
// .NET has no array deque; LinkedList<T> gives O(1) at both ends.
var dq = new LinkedList<int>();
dq.AddLast(1); dq.AddFirst(0);
int front = dq.First!.Value; dq.RemoveFirst();
int back = dq.Last!.Value; dq.RemoveLast();
```

### Monotonic stack and monotonic deque

Meta: category=data-structure | topic=monotonic-stack | languages=all | tags=next-greater-element, sliding-window-maximum, histogram | time=O(n) total | space=O(n)

A monotonic stack keeps elements in sorted order by popping everything that would break the order before each push. Every index is pushed and popped once, so a full pass is O(n). It answers next greater or smaller element, daily temperatures, and largest rectangle in a histogram. A monotonic deque applies the same rule with removal from the front when indices leave the window, giving sliding-window maximum in O(n).

#### Next greater element and sliding-window maximum — Python

```python
from collections import deque

def next_greater(nums):
    res, st = [-1] * len(nums), []        # st holds indices with decreasing values
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res

def window_max(nums, k):
    dq, out = deque(), []                  # dq holds indices with decreasing values
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

### Hash table

Meta: category=data-structure | topic=hash-table | languages=all | tags=hash-map, hash-set, collisions, load-factor, open-addressing, chaining | time=O(1) average, O(n) worst for get, put, delete | space=O(n)

A hash table maps a key to a bucket with `hash(key) mod capacity`. Collisions are resolved by separate chaining (each bucket holds a list) or open addressing (probe for the next free slot). When the load factor (entries ÷ capacity) passes a threshold, the table doubles and rehashes, keeping operations O(1) amortised. Worst case is O(n) when many keys collide, which attackers can force, so most runtimes randomise string hashes per process.

| Runtime | Collision strategy | Resize threshold | Iteration order |
| --- | --- | --- | --- |
| CPython `dict` | Open addressing with perturbed probing; compact index + entries array | \~2/3 full | Insertion order |
| V8 `Map` / `Set` (JavaScript, TypeScript) | Deterministic ordered hash tables | Implementation-defined | Insertion order |
| Java `HashMap` | Separate chaining; bucket becomes a red-black tree at 8 entries | 0.75 | Unspecified |
| .NET `Dictionary` | Separate chaining through index arrays | Grows when full, to the next prime size | Unspecified (insertion order until a removal, not guaranteed) |
| C++ `unordered_map` | Separate chaining with linked nodes | 1.0 | Unspecified |
| Go `map` | Swiss tables since Go 1.24 (earlier: 8-slot buckets with overflow chains) | 7/8 | Randomised on every range loop |
| Rust `HashMap` | SwissTable (hashbrown): SIMD group probing, SipHash-1-3 | 7/8 | Unspecified, randomised per run |
| Ruby `Hash` | Open addressing (2.4+); linear array for up to 8 entries | \~1/2 of bins | Insertion order |

#### Linear-probing hash map — Python

```python
class LinearProbeMap:
    _EMPTY, _TOMB = object(), object()

    def __init__(self, cap=8):
        self.keys = [self._EMPTY] * cap
        self.vals = [None] * cap
        self.n = 0

    def _slot(self, key):
        cap, i, tomb = len(self.keys), hash(key) % len(self.keys), None
        while self.keys[i] is not self._EMPTY:
            if self.keys[i] is self._TOMB:
                tomb = i if tomb is None else tomb
            elif self.keys[i] == key:
                return i, True
            i = (i + 1) % cap
        return (tomb if tomb is not None else i), False

    def put(self, key, val):
        if (self.n + 1) * 3 > len(self.keys) * 2:
            self._grow()
        i, found = self._slot(key)
        if not found:
            self.n += 1
        self.keys[i], self.vals[i] = key, val

    def get(self, key, default=None):
        i, found = self._slot(key)
        return self.vals[i] if found else default

    def remove(self, key):
        i, found = self._slot(key)
        if found:
            self.keys[i], self.vals[i] = self._TOMB, None
            self.n -= 1

    def _grow(self):
        live = [(k, v) for k, v in zip(self.keys, self.vals)
                if k is not self._EMPTY and k is not self._TOMB]
        self.keys = [self._EMPTY] * (len(self.keys) * 2)
        self.vals = [None] * len(self.keys)
        self.n = 0
        for k, v in live:
            self.put(k, v)
```

Deletion leaves a tombstone so later probes keep walking past it; an empty slot there would hide keys inserted after a collision.

#### FNV-1a string hash — C

```c
#include <stdint.h>

uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;
    while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ULL; }
    return h;
}
```

### Hash key requirements by language

Meta: category=data-structure | topic=hash-keys | languages=all | tags=hashable, equality, custom-keys, tuple-keys

A key must produce the same hash every time and equal keys must produce equal hashes; mutating a key after insertion makes it unreachable.

- **Python:** keys must be immutable and hashable (`tuple` yes, `list` no). Define `__hash__` and `__eq__` together, or use `@dataclass(frozen=True)`.
- **JavaScript:** `Map` compares objects by reference, so a new array `[1, 2]` never matches a stored `[1, 2]`. Encode composite keys as strings (`` `${r},${c}` ``) or numbers (`r * cols + c`).
- **TypeScript:** same runtime rule as JavaScript; type composite string keys with a template literal type (``Map<`${number},${number}`, V>``) so malformed keys fail to compile.
- **Java:** override `equals` and `hashCode` together, or use a `record`. Arrays hash by identity; wrap them with `List.of` or `Arrays.hashCode`.
- **C#:** override `Equals` and `GetHashCode` together, or use a `record` or value tuple `(int, int)`, which hash by value. Implement `IEquatable<T>` on structs to avoid boxing.
- **C:** you write the hash and equality functions; FNV-1a works for strings, and multiplying by a large odd constant works for integers.
- **C++:** custom keys need a `std::hash<T>` specialisation or a hasher functor plus `operator==`; `std::pair` and `std::tuple` have no default hash.
- **Go:** keys must be comparable types; arrays (`[2]int`) and structs (`struct{ r, c int }`) hash by value and make ideal composite keys, while slices, maps and functions cannot be keys. A `NaN` float key never matches itself, so each insert adds a new entry.
- **Rust:** `#[derive(Hash, PartialEq, Eq)]`; tuples and arrays of hashable types work directly; `f64` is not `Eq`, so floats need a wrapper such as `ordered-float`.
- **Ruby:** override `hash` and `eql?` together, or use `Struct` / `Data`, which do it for you. Unfrozen String keys are duplicated and frozen automatically; an Array key mutated after insertion cannot be found until `hash.rehash` runs.

### Hash table problem patterns

Meta: category=data-structure | topic=hashing-patterns | languages=all | tags=two-sum, frequency-count, anagram, prefix-sum, dedup | time=O(n) typical

| Pattern | Key → value | Example problems |
| --- | --- | --- |
| Complement lookup | value → index | Two sum, pairs with difference k |
| Frequency count | item → count | Top k frequent, valid anagram, majority element |
| Canonical grouping | sorted string or count tuple → list | Group anagrams, group shifted strings |
| Prefix sum index | prefix sum → count or first index | Subarray sum equals k, longest balanced subarray |
| Seen set | item → presence | Contains duplicate, longest consecutive sequence, cycle detection |
| Last position | item → last index | Longest substring without repeating characters |

#### Two sum and subarray sum equals k — Python

```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None

def subarray_sum_count(nums, k):
    count, prefix, freq = 0, 0, {0: 1}
    for x in nums:
        prefix += x
        count += freq.get(prefix - k, 0)
        freq[prefix] = freq.get(prefix, 0) + 1
    return count
```

### Binary tree traversals

Meta: category=data-structure | topic=tree-traversal | languages=all | tags=binary-tree, preorder, inorder, postorder, level-order, bfs, dfs | time=O(n) | space=O(h) recursive, O(w) level-order

A binary tree node has at most two children. Traversal order decides what each problem can compute; h is tree height and w is maximum level width.

| Order | Visit sequence | Typical use |
| --- | --- | --- |
| Pre-order | Node, left, right | Copy or serialise a tree, print a directory |
| In-order | Left, node, right | Sorted output from a BST, validate a BST |
| Post-order | Left, right, node | Delete a tree, compute heights, evaluate expression trees |
| Level-order | Breadth-first, level by level | Minimum depth, right-side view, zigzag order |

#### Iterative in-order and level-order traversal — Python

```python
from collections import deque

def inorder(root):                     # iterative: no recursion-depth limit
    out, st, node = [], [], root
    while st or node:
        while node:
            st.append(node); node = node.left
        node = st.pop()
        out.append(node.val)
        node = node.right
    return out

def level_order(root):
    if not root:
        return []
    res, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft(); level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        res.append(level)
    return res
```

### Binary search tree

Meta: category=data-structure | topic=binary-search-tree | languages=all | tags=bst, insert, delete, successor | time=O(h): O(log n) balanced, O(n) degenerate | space=O(n)

In a BST every key in the left subtree is smaller than the node and every key in the right subtree is larger, so search, insert and delete follow one root-to-leaf path. Sorted insertions degrade it into a linked list (h = n), which is why libraries use self-balancing trees. Deletion has three cases: a leaf is removed; a node with one child is spliced out; a node with two children takes its in-order successor's key, then the successor is deleted.

#### BST insert and delete — Python

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def bst_insert(root, key):
    if not root:
        return TreeNode(key)
    if key < root.val:
        root.left = bst_insert(root.left, key)
    elif key > root.val:
        root.right = bst_insert(root.right, key)
    return root

def bst_delete(root, key):
    if not root:
        return None
    if key < root.val:
        root.left = bst_delete(root.left, key)
    elif key > root.val:
        root.right = bst_delete(root.right, key)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = bst_delete(root.right, succ.val)
    return root
```

### Lowest common ancestor (LCA)

Meta: category=data-structure | topic=lowest-common-ancestor | languages=all | tags=tree, lca, binary-tree, bst, binary-lifting, node-distance | time=O(n) binary tree, O(h) BST, O(log n) per query with binary lifting after O(n log n) preprocessing | space=O(h) recursive, O(n log n) binary lifting

The lowest common ancestor of nodes p and q is the deepest node that has both as descendants, where a node counts as its own descendant. In a general binary tree, recurse: a node is the LCA if p and q are found in different subtrees, or if it is p or q itself and the other lies below it. In a BST, walk from the root: if both keys are smaller go left, if both are larger go right, otherwise the current node splits them and is the LCA. For many queries on a fixed tree, binary lifting stores every node's 2ʲ-th ancestor, lifts the deeper node to the same depth, then lifts both while their ancestors differ. The distance between two nodes is depth\[p\] + depth\[q\] − 2 × depth\[lca\].

#### Lowest common ancestor — Python

```python
def lca_binary_tree(root, p, q):           # p and q are nodes present in the tree
    if root is None or root is p or root is q:
        return root
    left = lca_binary_tree(root.left, p, q)
    right = lca_binary_tree(root.right, p, q)
    return root if left and right else left or right

def lca_bst(root, p, q):
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node
    return None

class BinaryLifting:                        # nodes 0..n-1; parent[root] == root
    def __init__(self, parent, depth):
        n = len(parent)
        self.log = max(1, n.bit_length())
        self.depth = depth
        self.up = [parent[:]]               # up[j][v] = 2^j-th ancestor of v
        for _ in range(1, self.log):
            prev = self.up[-1]
            self.up.append([prev[prev[v]] for v in range(n)])

    def lca(self, a, b):
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        diff = self.depth[a] - self.depth[b]
        for j in range(self.log):
            if (diff >> j) & 1:
                a = self.up[j][a]
        if a == b:
            return a
        for j in range(self.log - 1, -1, -1):
            if self.up[j][a] != self.up[j][b]:
                a, b = self.up[j][a], self.up[j][b]
        return self.up[0][a]
```

### Balanced search trees and ordered maps

Meta: category=data-structure | topic=balanced-bst | languages=java, csharp, cpp, rust | tags=red-black-tree, avl-tree, b-tree, treemap, sorted-map, floor, ceiling | time=O(log n) all operations | space=O(n)

Self-balancing trees keep height O(log n) under any insertion order and support ordered queries (floor, ceiling, range) that hash tables cannot.

| Tree | Balance rule | Trade-off | Used by |
| --- | --- | --- | --- |
| Red-black tree | No red node has a red child; every root-to-leaf path has equal black nodes | Fewer rotations, faster writes | Java `TreeMap`, C# `SortedDictionary`/`SortedSet`, C++ `std::map`/`std::set` |
| AVL tree | Subtree heights differ by at most 1 | Stricter balance, faster reads | Read-heavy indexes |
| B-tree | Each node holds many sorted keys; all leaves at the same depth | Cache- and disk-friendly | Rust `BTreeMap`/`BTreeSet`, database and filesystem indexes |

Ordered queries in languages that ship a sorted map (Python, JavaScript, TypeScript, Go and Ruby need a sorted array with binary search or a third-party package):

| Query | Java `TreeMap` | C# `SortedSet` | C++ `std::map` | Rust `BTreeMap` |
| --- | --- | --- | --- | --- |
| Smallest key ≥ x | `ceilingKey(x)` | `GetViewBetween(x, max).Min` | `lower_bound(x)` | `range(x..).next()` |
| Largest key ≤ x | `floorKey(x)` | `GetViewBetween(min, x).Max` | `prev(upper_bound(x))` | `range(..=x).next_back()` |
| Min / max | `firstKey()` / `lastKey()` | `Min` / `Max` | `begin()` / `rbegin()` | `first_key_value()` / `last_key_value()` |
| Keys in \[a, b) | `subMap(a, b)` | `GetViewBetween(a, b)` (inclusive) | `lower_bound(a)` to `lower_bound(b)` | `range(a..b)` |

### Trie

Meta: category=data-structure | topic=trie | languages=all | tags=prefix-tree, autocomplete, spell-checker, prefix-matching, word-search | time=O(k) insert and search for key length k | space=O(total characters × alphabet) worst case

A trie (prefix tree) stores strings character by character along root-to-node paths, so insert and lookup cost O(k) for a key of length k no matter how many keys are stored. Common patterns: autocomplete (walk to the prefix node, then collect every word beneath it), spell checking (exact lookup, or a walk that allows one insert, delete or replace to suggest words within edit distance 1), prefix matching and counting, word search on a grid with pruning, and longest common prefix. For lowercase ASCII, a fixed 26-slot child array per node is faster and smaller than a hash map per node.

#### Trie — Python

```python
class Trie:
    END = "$"                              # end-of-word marker key

    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def _walk(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node:
                return None
            node = node[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and self.END in node

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def autocomplete(self, prefix, limit=10):   # words with this prefix, alphabetical
        start, out = self._walk(prefix), []
        if start is None:
            return out
        stack = [(start, prefix)]
        while stack and len(out) < limit:
            node, word = stack.pop()
            if self.END in node:
                out.append(word)
            for ch in sorted((c for c in node if c != self.END), reverse=True):
                stack.append((node[ch], word + ch))
        return out
```

### Segment tree

Meta: category=data-structure | topic=segment-tree | languages=all | tags=range-query, range-sum, range-min, point-update, lazy-propagation | time=O(log n) query and update, O(n) build | space=O(2n) iterative, O(4n) recursive

A segment tree stores an aggregate (sum, min, max, gcd) for every range in a binary partition of the array. Any range query combines O(log n) stored nodes; a point update refreshes one leaf-to-root path. Lazy propagation defers range updates so they also cost O(log n). Choose it over a Fenwick tree when the operation is not invertible (min, max).

#### Iterative segment tree for range sum — Python

```python
class SegTree:                          # 0-indexed, query covers [l, r)
    def __init__(self, arr):
        self.n = len(arr)
        self.t = [0] * self.n + list(arr)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def update(self, i, val):
        i += self.n
        self.t[i] = val
        while i > 1:
            i //= 2
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def query(self, l, r):
        res, l, r = 0, l + self.n, r + self.n
        while l < r:
            if l & 1: res += self.t[l]; l += 1
            if r & 1: r -= 1; res += self.t[r]
            l //= 2; r //= 2
        return res
```

### Fenwick tree (binary indexed tree)

Meta: category=data-structure | topic=fenwick-tree | languages=all | tags=bit, prefix-sum, point-update, inversion-count | time=O(log n) update and prefix query | space=O(n)

A Fenwick tree stores partial sums where index i covers a range of length `i & -i` (its lowest set bit). Updates climb by adding the lowest set bit; prefix queries descend by subtracting it. It is smaller and faster than a segment tree but needs an invertible operation (sum, xor) to answer arbitrary ranges as `prefix(r) - prefix(l - 1)`. Also used to count inversions in O(n log n).

#### Fenwick tree — Python

```python
class Fenwick:                          # public API 0-indexed, internal array 1-indexed
    def __init__(self, n):
        self.t = [0] * (n + 1)

    def add(self, i, delta):
        i += 1
        while i < len(self.t):
            self.t[i] += delta
            i += i & -i

    def prefix(self, i):                # sum of elements [0, i]
        i += 1
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i
        return s
```

### Binary heap and priority queue

Meta: category=data-structure | topic=binary-heap | languages=all | tags=priority-queue, min-heap, max-heap, heapify, top-k | time=O(1) peek, O(log n) push and pop, O(n) heapify | space=O(n)

A binary heap is a complete binary tree stored in an array: children of index i are at 2i+1 and 2i+2, its parent at (i−1)/2 rounded down. In a min-heap every parent is ≤ its children. Push appends and sifts up; pop swaps the root with the last element, removes it, and sifts down. Building a heap from n items bottom-up is O(n). Uses: Dijkstra, Prim, task scheduling, and the top K, k-way merge and two-heap patterns covered in the heap patterns chunk.

| Language | Type | Default order | Opposite order |
| --- | --- | --- | --- |
| Python | `heapq` functions on a `list` | Min | Push negated keys or `(-priority, item)` |
| JavaScript | Build | — | Swap the comparator |
| TypeScript | Build a generic `Heap<T>` | — | Swap the comparator |
| Java | `PriorityQueue<T>` | Min | `Comparator.reverseOrder()` |
| C# | `PriorityQueue<TElement, TPriority>` | Min | `Comparer<int>.Create((a, b) => b.CompareTo(a))` |
| C | Build | — | Flip the comparison |
| C++ | `std::priority_queue<T>` | Max | `std::greater<T>` |
| Go | `container/heap` over a type implementing `heap.Interface` | Min when `Less` uses `<` | Make `Less` use `>` |
| Rust | `BinaryHeap<T>` | Max | Wrap in `std::cmp::Reverse` |
| Ruby | Build | — | Swap the comparator block |

#### Binary heap — Python

```python
import heapq

h = []
heapq.heappush(h, (2, "b"))
heapq.heappush(h, (1, "a"))
priority, item = heapq.heappop(h)      # (1, 'a')
heapq.heapify(nums)                    # O(n), in place
top3 = heapq.nlargest(3, nums)         # O(n log k)
```

#### Binary heap — JavaScript

```javascript
class Heap {
  constructor(cmp = (a, b) => a - b) { this.a = []; this.cmp = cmp; }
  get size() { return this.a.length; }
  peek() { return this.a[0]; }
  push(x) {
    const a = this.a; a.push(x); let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this.cmp(a[i], a[p]) >= 0) break;
      [a[i], a[p]] = [a[p], a[i]]; i = p;
    }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last; let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1; let m = i;
        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]]; i = m;
      }
    }
    return top;
  }
}
```

#### Binary heap — TypeScript

```typescript
class Heap<T> {
  private readonly a: T[] = [];
  constructor(private readonly cmp: (x: T, y: T) => number) {}

  get size(): number { return this.a.length; }
  peek(): T | undefined { return this.a[0]; }

  push(x: T): void {
    const a = this.a;
    a.push(x);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (this.cmp(a[i], a[p]) >= 0) break;
      [a[i], a[p]] = [a[p], a[i]];
      i = p;
    }
  }

  pop(): T | undefined {
    const a = this.a;
    if (a.length === 0) return undefined;
    const top = a[0];
    const last = a.pop()!;
    if (a.length > 0) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && this.cmp(a[l], a[m]) < 0) m = l;
        if (r < a.length && this.cmp(a[r], a[m]) < 0) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]];
        i = m;
      }
    }
    return top;
  }
}

const minHeap = new Heap<number>((a, b) => a - b);
const maxHeap = new Heap<[priority: number, id: string]>((x, y) => y[0] - x[0]);
```

#### Binary heap — Java

```java
PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> Integer.compare(x[0], y[0]));
pq.offer(new int[]{2, 7});
int[] top = pq.poll();                 // smallest x[0]
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
```

#### Binary heap — C#

```csharp
var pq = new PriorityQueue<string, int>();   // element, priority
pq.Enqueue("b", 2);
pq.Enqueue("a", 1);
string first = pq.Dequeue();                 // "a"
var maxPq = new PriorityQueue<string, int>(Comparer<int>.Create((a, b) => b.CompareTo(a)));
```

#### Binary heap — C

```c
static void swap_int(int *a, int *b) { int t = *a; *a = *b; *b = t; }

void heap_push(int *h, int *n, int x) {       /* min-heap in h[0..*n) */
    int i = (*n)++; h[i] = x;
    while (i && h[(i - 1) / 2] > h[i]) { swap_int(&h[i], &h[(i - 1) / 2]); i = (i - 1) / 2; }
}

int heap_pop(int *h, int *n) {
    int top = h[0]; h[0] = h[--(*n)]; int i = 0;
    for (;;) {
        int l = 2 * i + 1, r = l + 1, m = i;
        if (l < *n && h[l] < h[m]) m = l;
        if (r < *n && h[r] < h[m]) m = r;
        if (m == i) break;
        swap_int(&h[i], &h[m]); i = m;
    }
    return top;
}
```

#### Binary heap — C++

```cpp
std::priority_queue<int> maxh;
maxh.push(5); int m = maxh.top(); maxh.pop();

using P = std::pair<int, int>;
std::priority_queue<P, std::vector<P>, std::greater<P>> minh;   // min-heap of pairs
minh.push({1, 42});
```

#### Binary heap — Go

```go
import "container/heap"

type Item struct {
	prio int
	val  string
}

// MinHeap implements heap.Interface; make Less use > for a max-heap.
type MinHeap []Item

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i].prio < h[j].prio }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x any)        { *h = append(*h, x.(Item)) }
func (h *MinHeap) Pop() any {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[:n-1]
	return x
}

func example() {
	h := &MinHeap{{2, "b"}, {1, "a"}}
	heap.Init(h)                  // O(n)
	heap.Push(h, Item{0, "z"})    // O(log n)
	top := heap.Pop(h).(Item)     // {0 z}
	_ = top
}
```

#### Binary heap — Rust

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

let mut h = BinaryHeap::new();                // max-heap
h.push(Reverse((2, "b")));                    // Reverse turns it into a min-heap
h.push(Reverse((1, "a")));
if let Some(Reverse((priority, item))) = h.pop() { /* (1, "a") */ }
```

#### Binary heap — Ruby

```ruby
class Heap
  def initialize(&cmp)
    @a = []
    @cmp = cmp || ->(x, y) { x <=> y }
  end

  def size = @a.size
  def peek = @a.first

  def push(x)
    @a << x
    i = @a.size - 1
    while i > 0
      p = (i - 1) / 2
      break if @cmp.call(@a[i], @a[p]) >= 0
      @a[i], @a[p] = @a[p], @a[i]
      i = p
    end
    self
  end

  def pop
    return nil if @a.empty?
    top = @a.first
    last = @a.pop
    unless @a.empty?
      @a[0] = last
      i = 0
      loop do
        l, r, m = 2 * i + 1, 2 * i + 2, i
        m = l if l < @a.size && @cmp.call(@a[l], @a[m]) < 0
        m = r if r < @a.size && @cmp.call(@a[r], @a[m]) < 0
        break if m == i
        @a[i], @a[m] = @a[m], @a[i]
        i = m
      end
    end
    top
  end
end

min_heap = Heap.new
max_heap = Heap.new { |x, y| y <=> x }
```

### Heap patterns: top K, merge K sorted lists, two heaps

Meta: category=data-structure | topic=heap-patterns | languages=all | tags=top-k, kth-largest, merge-k-sorted-lists, k-way-merge, two-heaps, running-median | time=top K O(n log k); k-way merge O(N log k); median O(log n) insert, O(1) query | space=O(k) or O(n)

- **Top K elements:** scan once while keeping a min-heap of size k; whenever it grows past k, pop the smallest. The heap ends with the k largest items and its root is the k-th largest, in O(n log k) time and O(k) space. Use a max-heap (or reversed comparator) for the k smallest. Problems: kth largest element, top K frequent elements, K closest points to origin.
- **Merge K sorted lists (k-way merge):** push the first element of each list with its list index; repeatedly pop the smallest, output it, and push the next element from the same list. N total elements cost O(N log k). Problems: merge k sorted lists, smallest range covering k lists, kth smallest in a sorted matrix.
- **Two heaps:** a max-heap holds the lower half and a min-heap the upper half, rebalanced after each insert so their sizes differ by at most one. The median is the larger heap's root, or the mean of both roots. Problems: find median from a data stream, sliding window median, maximise capital (IPO).

Put a unique tie-breaker (such as the list index) in heap tuples so equal keys never fall through to comparing incomparable payloads.

#### Top K, k-way merge and running median — Python

```python
import heapq

def kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)              # drop the smallest; keep the k largest
    return heap[0]

def merge_k_sorted(lists):                   # lists: sorted Python lists
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out

class MedianFinder:
    def __init__(self):
        self.low = []                        # max-heap of the lower half (negated values)
        self.high = []                       # min-heap of the upper half

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

### Graph representations

Meta: category=data-structure | topic=graph-representation | languages=all | tags=adjacency-list, adjacency-matrix, edge-list, csr, grid-graph | space=O(V + E) list, O(V²) matrix

A graph is a set of vertices joined by edges, directed or undirected, weighted or not. Store sparse graphs (E much smaller than V²) as adjacency lists and dense ones as matrices. A grid is an implicit graph whose neighbours are the four offsets `(1,0), (-1,0), (0,1), (0,-1)`.

| Representation | Space | Edge check | Iterate neighbours | Best for |
| --- | --- | --- | --- | --- |
| Adjacency list | O(V + E) | O(degree) | O(degree) | Most real graphs, BFS, DFS, Dijkstra |
| Adjacency matrix | O(V²) | O(1) | O(V) | Dense graphs, Floyd-Warshall |
| Edge list | O(E) | O(E) | O(E) | Kruskal, Bellman-Ford |
| CSR (compressed sparse row) | O(V + E) | O(log degree) if sorted | O(degree), cache-friendly | Large static graphs |

#### Weighted adjacency list — all languages

```text
Python      adj = [[] for _ in range(n)];                       adj[u].append((v, w))
JavaScript  const adj = Array.from({ length: n }, () => []);      adj[u].push([v, w]);
TypeScript  const adj: [number, number][][] = Array.from({ length: n }, () => []);  adj[u].push([v, w]);
Java        List<List<int[]>> adj = new ArrayList<>(); for (int i = 0; i < n; i++) adj.add(new ArrayList<>());  adj.get(u).add(new int[]{v, w});
C#          var adj = new List<(int to, int w)>[n]; for (int i = 0; i < n; i++) adj[i] = new();  adj[u].Add((v, w));
C           struct Edge { int to, w, next; }; int head[N]; /* forward-star: head[] = -1, edges appended to an array */
C++         std::vector<std::vector<std::pair<int, int>>> adj(n);   adj[u].push_back({v, w});
Go          type Edge struct{ to, w int }; adj := make([][]Edge, n);  adj[u] = append(adj[u], Edge{v, w})
Rust        let mut adj: Vec<Vec<(usize, i64)>> = vec![vec![]; n];   adj[u].push((v, w));
Ruby        adj = Array.new(n) { [] };                               adj[u] << [v, w]
```

### Union-find (disjoint set union)

Meta: category=data-structure | topic=union-find | languages=all | tags=dsu, disjoint-set, path-compression, union-by-size, connected-components, kruskal | time=O(α(n)) per operation, effectively constant | space=O(n)

Union-find tracks which elements belong to the same group under merges. `find` returns a group's representative; `union` links two representatives. Path compression (or path halving) flattens trees during `find`, and union by size attaches the smaller tree under the larger; together they make each operation O(α(n)), where α is the inverse Ackermann function (≤ 4 for any practical n). Uses: Kruskal's MST, cycle detection in undirected graphs, number of connected components, accounts merge, redundant connection.

#### Union-find — Python

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n)); self.sz = [1] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]      # path halving
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.sz[a] < self.sz[b]:
            a, b = b, a
        self.p[b] = a; self.sz[a] += self.sz[b]
        return True
```

#### Union-find — JavaScript

```javascript
class DSU {
  constructor(n) { this.p = Array.from({ length: n }, (_, i) => i); this.sz = new Array(n).fill(1); }
  find(x) { while (this.p[x] !== x) { this.p[x] = this.p[this.p[x]]; x = this.p[x]; } return x; }
  union(a, b) {
    a = this.find(a); b = this.find(b);
    if (a === b) return false;
    if (this.sz[a] < this.sz[b]) [a, b] = [b, a];
    this.p[b] = a; this.sz[a] += this.sz[b];
    return true;
  }
}
```

#### Union-find — TypeScript

```typescript
class DSU {
  private readonly parent: number[];
  private readonly size: number[];

  constructor(n: number) {
    this.parent = Array.from({ length: n }, (_, i) => i);
    this.size = new Array<number>(n).fill(1);
  }

  find(x: number): number {
    while (this.parent[x] !== x) {
      this.parent[x] = this.parent[this.parent[x]];
      x = this.parent[x];
    }
    return x;
  }

  union(a: number, b: number): boolean {
    a = this.find(a);
    b = this.find(b);
    if (a === b) return false;
    if (this.size[a] < this.size[b]) [a, b] = [b, a];
    this.parent[b] = a;
    this.size[a] += this.size[b];
    return true;
  }
}
```

#### Union-find — Java

```java
class DSU {
    private final int[] p, sz;
    DSU(int n) { p = new int[n]; sz = new int[n]; for (int i = 0; i < n; i++) { p[i] = i; sz[i] = 1; } }
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    boolean union(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) { int t = a; a = b; b = t; }
        p[b] = a; sz[a] += sz[b];
        return true;
    }
}
```

#### Union-find — C#

```csharp
class DSU {
    private readonly int[] p, sz;
    public DSU(int n) { p = new int[n]; sz = new int[n]; for (int i = 0; i < n; i++) { p[i] = i; sz[i] = 1; } }
    public int Find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    public bool Union(int a, int b) {
        a = Find(a); b = Find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) (a, b) = (b, a);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
}
```

#### Union-find — C

```c
#include <stdlib.h>

typedef struct { int *p, *sz; } DSU;

DSU dsu_new(int n) {
    DSU d = { malloc(n * sizeof(int)), malloc(n * sizeof(int)) };
    for (int i = 0; i < n; i++) { d.p[i] = i; d.sz[i] = 1; }
    return d;
}
int dsu_find(DSU *d, int x) { while (d->p[x] != x) { d->p[x] = d->p[d->p[x]]; x = d->p[x]; } return x; }
int dsu_union(DSU *d, int a, int b) {
    a = dsu_find(d, a); b = dsu_find(d, b);
    if (a == b) return 0;
    if (d->sz[a] < d->sz[b]) { int t = a; a = b; b = t; }
    d->p[b] = a; d->sz[a] += d->sz[b];
    return 1;
}
void dsu_free(DSU *d) { free(d->p); free(d->sz); }
```

#### Union-find — C++

```cpp
struct DSU {
    std::vector<int> p, sz;
    explicit DSU(int n) : p(n), sz(n, 1) { std::iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) std::swap(a, b);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};
```

#### Union-find — Go

```go
type DSU struct{ parent, size []int }

func NewDSU(n int) *DSU {
	d := &DSU{parent: make([]int, n), size: make([]int, n)}
	for i := range n {
		d.parent[i], d.size[i] = i, 1
	}
	return d
}

func (d *DSU) Find(x int) int {
	for d.parent[x] != x {
		d.parent[x] = d.parent[d.parent[x]]
		x = d.parent[x]
	}
	return x
}

func (d *DSU) Union(a, b int) bool {
	a, b = d.Find(a), d.Find(b)
	if a == b {
		return false
	}
	if d.size[a] < d.size[b] {
		a, b = b, a
	}
	d.parent[b] = a
	d.size[a] += d.size[b]
	return true
}
```

#### Union-find — Rust

```rust
struct Dsu { p: Vec<usize>, sz: Vec<usize> }

impl Dsu {
    fn new(n: usize) -> Self { Self { p: (0..n).collect(), sz: vec![1; n] } }
    fn find(&mut self, mut x: usize) -> usize {
        while self.p[x] != x { self.p[x] = self.p[self.p[x]]; x = self.p[x]; }
        x
    }
    fn union(&mut self, a: usize, b: usize) -> bool {
        let (mut a, mut b) = (self.find(a), self.find(b));
        if a == b { return false; }
        if self.sz[a] < self.sz[b] { std::mem::swap(&mut a, &mut b); }
        self.p[b] = a; self.sz[a] += self.sz[b];
        true
    }
}
```

#### Union-find — Ruby

```ruby
class DSU
  def initialize(n)
    @p = (0...n).to_a
    @sz = Array.new(n, 1)
  end

  def find(x)
    while @p[x] != x
      @p[x] = @p[@p[x]]
      x = @p[x]
    end
    x
  end

  def union(a, b)
    a, b = find(a), find(b)
    return false if a == b
    a, b = b, a if @sz[a] < @sz[b]
    @p[b] = a
    @sz[a] += @sz[b]
    true
  end
end
```

### LRU cache

Meta: category=data-structure | topic=lru-cache | languages=all | tags=least-recently-used, hash-map, doubly-linked-list, eviction, cache | time=O(1) get and put | space=O(capacity)

An LRU cache evicts the least recently used entry when full. A hash map from key to list node gives O(1) lookup; a doubly linked list ordered by recency gives O(1) move-to-front and O(1) eviction from the tail. Built-in shortcuts: Python `OrderedDict` (or `@functools.lru_cache` for memoising functions), Java `LinkedHashMap` in access-order mode, and the insertion-ordered `Map` in JavaScript and TypeScript or `Hash` in Ruby (delete then re-insert moves a key to the end; the first key is the oldest). In C++ pair `std::list` with `std::unordered_map<K, std::list<...>::iterator>` and move nodes with `splice`; in C# pair `LinkedList<T>` with `Dictionary<K, LinkedListNode<T>>`; in Go pair `container/list` with `map[K]*list.Element` and call `MoveToFront`; in Rust use an index-based arena or the `lru` crate.

#### LRU cache — Python

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)
```

#### LRU cache — Java

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int cap;
    LRUCache(int cap) { super(16, 0.75f, true); this.cap = cap; }   // true = access order
    @Override protected boolean removeEldestEntry(Map.Entry<K, V> eldest) { return size() > cap; }
}
```

### Bloom filter

Meta: category=data-structure | topic=bloom-filter | languages=all | tags=probabilistic, membership, false-positive, bit-array | time=O(k) insert and query for k hash functions | space=O(m) bits

A Bloom filter is a bit array of m bits with k hash functions. Insert sets k bits; a query reports "definitely absent" if any of the k bits is 0, else "probably present". It never gives false negatives and cannot delete (a counting Bloom filter can). False-positive rate ≈ (1 − e^(−kn/m))^k for n inserted items; the optimal k = (m/n)·ln 2. At 10 bits per element with k = 7 the rate is about 0.8%. Databases such as RocksDB and Cassandra use it to skip disk reads for missing keys.

### Skip list

Meta: category=data-structure | topic=skip-list | languages=all | tags=probabilistic, sorted, concurrent, express-lanes | time=O(log n) expected search, insert, delete | space=O(n) expected

A skip list is a sorted linked list with extra levels of forward pointers. Each node is promoted to the next level with probability 1/2, so higher levels act as express lanes and a search drops down level by level in O(log n) expected time. It is simpler than a balanced tree to make lock-free, which is why Redis sorted sets and Java's `ConcurrentSkipListMap` use it.

## Algorithms

Each chunk explains one algorithm, its complexity and when to use it; anchor algorithms carry code in all ten languages.

### Sorting algorithm comparison

Meta: category=algorithm | topic=sorting-comparison | languages=all | tags=sorting, stability, in-place, timsort, introsort, pdqsort

Comparison sorts cannot beat O(n log n) in the worst case; counting and radix sort beat it by exploiting small integer keys. A stable sort keeps equal keys in their original order, which matters when sorting by several keys in sequence.

| Algorithm | Best | Average | Worst | Extra space | Stable | Use when |
| --- | --- | --- | --- | --- | --- | --- |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) | Yes | n < \~16, nearly sorted data |
| Selection sort | O(n²) | O(n²) | O(n²) | O(1) | No | Minimising swaps |
| Bubble sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Teaching only |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Linked lists, external sorting, stability required |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) | No | General in-memory sorting with random pivots |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No | Guaranteed O(n log n) with O(1) space |
| Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes | Integer keys in a small range k |
| Radix sort (LSD) | O(d(n + b)) | O(d(n + b)) | O(d(n + b)) | O(n + b) | Yes | Fixed-width integers or strings, d digits in base b |
| Timsort | O(n) | O(n log n) | O(n log n) | O(n) | Yes | Real-world data with runs (Python, Java objects, V8) |
| Introsort | O(n log n) | O(n log n) | O(n log n) | O(log n) | No | Quicksort that falls back to heap sort (C++ `std::sort`, .NET `Array.Sort`) |
| Pattern-defeating quicksort | O(n) | O(n log n) | O(n log n) | O(log n) | No | Go `slices.Sort` and `sort.Slice`; Rust `sort_unstable` uses ipnsort, a pdqsort descendant |

### Merge sort

Meta: category=algorithm | topic=merge-sort | languages=all | tags=sorting, divide-and-conquer, stable, inversions | time=O(n log n) all cases | space=O(n)

Merge sort splits the array in half, sorts each half recursively, then merges the two sorted halves by repeatedly taking the smaller front element. The recursion depth is log n and each level does O(n) merging work. It is stable and has no bad inputs, but needs O(n) auxiliary space. Counting inversions is a small extension: when an element from the right half is taken, add the number of elements left in the left half.

#### Merge sort — Python

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]
```

#### Merge sort — JavaScript

```javascript
function mergeSort(a) {
  if (a.length <= 1) return a;
  const mid = a.length >> 1;
  const l = mergeSort(a.slice(0, mid)), r = mergeSort(a.slice(mid));
  const out = []; let i = 0, j = 0;
  while (i < l.length && j < r.length) out.push(l[i] <= r[j] ? l[i++] : r[j++]);
  return out.concat(l.slice(i), r.slice(j));
}
```

#### Merge sort — TypeScript

```typescript
function mergeSort<T>(a: readonly T[], cmp: (x: T, y: T) => number): T[] {
  if (a.length <= 1) return a.slice();
  const mid = a.length >> 1;
  const l = mergeSort(a.slice(0, mid), cmp);
  const r = mergeSort(a.slice(mid), cmp);
  const out: T[] = [];
  let i = 0, j = 0;
  while (i < l.length && j < r.length) out.push(cmp(l[i], r[j]) <= 0 ? l[i++] : r[j++]);
  return out.concat(l.slice(i), r.slice(j));
}

const sorted = mergeSort([5, 2, 9, 1], (x, y) => x - y);   // [1, 2, 5, 9]
```

#### Merge sort — Java

```java
static void mergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    mergeSort(a, tmp, lo, mid); mergeSort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo);
}
```

#### Merge sort — C#

```csharp
static void MergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    MergeSort(a, tmp, lo, mid); MergeSort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    Array.Copy(tmp, lo, a, lo, hi - lo);
}
```

#### Merge sort — C

```c
#include <string.h>

void merge_sort(int *a, int *tmp, int lo, int hi) {         /* sorts a[lo, hi) */
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, tmp, lo, mid); merge_sort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = a[i] <= a[j] ? a[i++] : a[j++];
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    memcpy(a + lo, tmp + lo, (hi - lo) * sizeof *a);
}
```

#### Merge sort — C++

```cpp
void merge_sort(std::vector<int>& a, std::vector<int>& tmp, int lo, int hi) {
    if (hi - lo < 2) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, tmp, lo, mid); merge_sort(a, tmp, mid, hi);
    std::merge(a.begin() + lo, a.begin() + mid, a.begin() + mid, a.begin() + hi, tmp.begin() + lo);
    std::copy(tmp.begin() + lo, tmp.begin() + hi, a.begin() + lo);
}
```

#### Merge sort — Go

```go
// mergeSort sorts a in place; tmp must have len(tmp) >= len(a).
func mergeSort(a, tmp []int) {
	n := len(a)
	if n < 2 {
		return
	}
	mid := n / 2
	mergeSort(a[:mid], tmp)
	mergeSort(a[mid:], tmp)
	i, j, k := 0, mid, 0
	for i < mid && j < n {
		if a[i] <= a[j] {
			tmp[k] = a[i]
			i++
		} else {
			tmp[k] = a[j]
			j++
		}
		k++
	}
	k += copy(tmp[k:], a[i:mid])
	copy(tmp[k:], a[j:])
	copy(a, tmp[:n])
}

// Usage: mergeSort(nums, make([]int, len(nums)))
```

#### Merge sort — Rust

```rust
fn merge_sort<T: PartialOrd + Copy>(a: &mut [T]) {
    let n = a.len();
    if n < 2 { return; }
    let mid = n / 2;
    merge_sort(&mut a[..mid]);
    merge_sort(&mut a[mid..]);
    let mut out = Vec::with_capacity(n);
    let (mut i, mut j) = (0, mid);
    while i < mid && j < n {
        if a[i] <= a[j] { out.push(a[i]); i += 1; } else { out.push(a[j]); j += 1; }
    }
    out.extend_from_slice(&a[i..mid]);
    out.extend_from_slice(&a[j..]);
    a.copy_from_slice(&out);
}
```

#### Merge sort — Ruby

```ruby
def merge_sort(a)
  return a if a.size <= 1
  mid = a.size / 2
  left, right = merge_sort(a[0...mid]), merge_sort(a[mid..])
  out, i, j = [], 0, 0
  while i < left.size && j < right.size
    if left[i] <= right[j]
      out << left[i]; i += 1
    else
      out << right[j]; j += 1
    end
  end
  out.concat(left[i..], right[j..])
end
```

### Quicksort

Meta: category=algorithm | topic=quicksort | languages=all | tags=sorting, divide-and-conquer, partition, lomuto, hoare, in-place | time=O(n log n) average, O(n²) worst | space=O(log n) average stack

Quicksort picks a pivot, partitions the array so smaller elements come before it and larger ones after, then recurses on both sides. A random pivot makes the O(n²) worst case (already-sorted input with a first-element pivot) vanishingly unlikely. It sorts in place and is not stable. The Lomuto partition below is the clearest; Hoare partition does about three times fewer swaps, and three-way partitioning (Dutch national flag) handles many duplicate keys in O(n). Recursing into the smaller side first bounds stack depth at O(log n).

#### Quicksort — Python

```python
import random

def quicksort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]
    quicksort(a, lo, i - 1)
    quicksort(a, i + 1, hi)
```

#### Quicksort — JavaScript

```javascript
function quicksort(a, lo = 0, hi = a.length - 1) {
  if (lo >= hi) return;
  const r = lo + Math.floor(Math.random() * (hi - lo + 1));
  [a[r], a[hi]] = [a[hi], a[r]];
  const pivot = a[hi]; let i = lo;
  for (let j = lo; j < hi; j++) if (a[j] < pivot) { [a[i], a[j]] = [a[j], a[i]]; i++; }
  [a[i], a[hi]] = [a[hi], a[i]];
  quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — TypeScript

```typescript
function quicksort<T>(a: T[], cmp: (x: T, y: T) => number, lo = 0, hi = a.length - 1): void {
  if (lo >= hi) return;
  const r = lo + Math.floor(Math.random() * (hi - lo + 1));
  [a[r], a[hi]] = [a[hi], a[r]];
  const pivot = a[hi];
  let i = lo;
  for (let j = lo; j < hi; j++) {
    if (cmp(a[j], pivot) < 0) {
      [a[i], a[j]] = [a[j], a[i]];
      i++;
    }
  }
  [a[i], a[hi]] = [a[hi], a[i]];
  quicksort(a, cmp, lo, i - 1);
  quicksort(a, cmp, i + 1, hi);
}

const nums = [5, 2, 9, 1];
quicksort(nums, (x, y) => x - y);   // nums is now [1, 2, 5, 9]
```

#### Quicksort — Java

```java
static void quicksort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int r = java.util.concurrent.ThreadLocalRandom.current().nextInt(lo, hi + 1);
    int t = a[r]; a[r] = a[hi]; a[hi] = t;
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) { t = a[i]; a[i] = a[j]; a[j] = t; i++; }
    t = a[i]; a[i] = a[hi]; a[hi] = t;
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — C#

```csharp
static void QuickSort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int r = Random.Shared.Next(lo, hi + 1);
    (a[r], a[hi]) = (a[hi], a[r]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) { (a[i], a[j]) = (a[j], a[i]); i++; }
    (a[i], a[hi]) = (a[hi], a[i]);
    QuickSort(a, lo, i - 1); QuickSort(a, i + 1, hi);
}
```

#### Quicksort — C

```c
#include <stdlib.h>

static void swap_int(int *x, int *y) { int t = *x; *x = *y; *y = t; }

void quicksort(int *a, int lo, int hi) {
    if (lo >= hi) return;
    swap_int(&a[lo + rand() % (hi - lo + 1)], &a[hi]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; j++) if (a[j] < pivot) swap_int(&a[i++], &a[j]);
    swap_int(&a[i], &a[hi]);
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — C++

```cpp
void quicksort(std::vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    static std::mt19937 rng(std::random_device{}());
    std::swap(a[std::uniform_int_distribution<int>(lo, hi)(rng)], a[hi]);
    int pivot = a[hi], i = lo;
    for (int j = lo; j < hi; ++j) if (a[j] < pivot) std::swap(a[i++], a[j]);
    std::swap(a[i], a[hi]);
    quicksort(a, lo, i - 1); quicksort(a, i + 1, hi);
}
```

#### Quicksort — Go

```go
import "math/rand/v2"

func quicksort(a []int) {
	if len(a) < 2 {
		return
	}
	hi := len(a) - 1
	r := rand.IntN(len(a))
	a[r], a[hi] = a[hi], a[r]
	pivot, i := a[hi], 0
	for j := 0; j < hi; j++ {
		if a[j] < pivot {
			a[i], a[j] = a[j], a[i]
			i++
		}
	}
	a[i], a[hi] = a[hi], a[i]
	quicksort(a[:i])     // sub-slices share the backing array, so sorting is in place
	quicksort(a[i+1:])
}
```

#### Quicksort — Rust

```rust
fn quicksort<T: PartialOrd>(a: &mut [T]) {
    let n = a.len();
    if n < 2 { return; }
    a.swap(n / 2, n - 1);                 // middle pivot; std has no RNG, use the rand crate for random
    let mut i = 0;
    for j in 0..n - 1 {
        if a[j] < a[n - 1] { a.swap(i, j); i += 1; }
    }
    a.swap(i, n - 1);
    let (left, right) = a.split_at_mut(i);
    quicksort(left);
    quicksort(&mut right[1..]);
}
```

#### Quicksort — Ruby

```ruby
def quicksort(a, lo = 0, hi = a.size - 1)
  return a if lo >= hi
  r = rand(lo..hi)
  a[r], a[hi] = a[hi], a[r]
  pivot, i = a[hi], lo
  (lo...hi).each do |j|
    next unless a[j] < pivot
    a[i], a[j] = a[j], a[i]
    i += 1
  end
  a[i], a[hi] = a[hi], a[i]
  quicksort(a, lo, i - 1)
  quicksort(a, i + 1, hi)
  a
end
```

### Quickselect (k-th smallest element)

Meta: category=algorithm | topic=quickselect | languages=all | tags=selection, kth-largest, partition, median | time=O(n) average, O(n²) worst | space=O(1) iterative

Quickselect partitions like quicksort but continues into only the side that contains index k, so the expected work is n + n/2 + n/4 + … = O(n). Library versions: C++ `std::nth_element`, Rust `select_nth_unstable`. A size-k heap (O(n log k)) is the alternative when data streams in. Median of medians guarantees O(n) worst case but is slower in practice.

#### Quickselect — Python

```python
import random

def quickselect(a, k):                  # k-th smallest, 0-indexed; mutates a
    lo, hi = 0, len(a) - 1
    while True:
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]; i += 1
        a[i], a[hi] = a[hi], a[i]
        if i == k:
            return a[i]
        if i < k:
            lo = i + 1
        else:
            hi = i - 1
```

### Insertion sort and heap sort

Meta: category=algorithm | topic=insertion-sort-heap-sort | languages=all | tags=sorting, in-place, small-arrays, heapify | time=insertion O(n²) worst and O(n) nearly sorted; heap sort O(n log n) | space=O(1)

Insertion sort shifts each element left until it is in place; it is the fastest choice for tiny or nearly sorted arrays, which is why hybrid sorts (Timsort, introsort) use it for small runs. Heap sort builds a max-heap in O(n), then repeatedly swaps the maximum to the end and sifts down, giving guaranteed O(n log n) with O(1) extra space.

#### Insertion sort and heap sort — Python

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0 and a[j] > x:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = x

def heap_sort(a):
    def sift(i, n):
        while (c := 2 * i + 1) < n:
            if c + 1 < n and a[c + 1] > a[c]:
                c += 1
            if a[i] >= a[c]:
                return
            a[i], a[c] = a[c], a[i]; i = c
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(0, end)
```

### Counting sort and radix sort

Meta: category=algorithm | topic=counting-radix-sort | languages=all | tags=non-comparison-sort, integer-sort, bucket, lsd | time=counting O(n + k); radix O(d(n + b)) | space=O(n + k)

Counting sort tallies how often each key in the range \[0, k\] occurs, then emits keys in order; it is linear when k is O(n). Radix sort (least significant digit first) applies a stable counting pass per digit, so d passes in base b sort fixed-width integers or strings in linear time. Bucket sort distributes uniformly distributed floats into n buckets and sorts each, O(n) on average.

#### Counting sort and radix sort — Python

```python
def counting_sort(a, max_val):          # non-negative integers ≤ max_val
    count = [0] * (max_val + 1)
    for x in a:
        count[x] += 1
    return [v for v, c in enumerate(count) for _ in range(c)]

def radix_sort(a):                      # LSD, base 10, non-negative integers
    exp = 1
    while a and max(a) // exp:
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = [x for b in buckets for x in b]
        exp *= 10
    return a
```

### Binary search

Meta: category=algorithm | topic=binary-search | languages=all | tags=searching, lower-bound, upper-bound, sorted-array, overflow | time=O(log n) | space=O(1)

Binary search halves a sorted range each step. The safest template finds the lower bound: the first index in the half-open range \[lo, hi) where `a[i] >= target`, returning the array length when every element is smaller. It cannot loop forever because the range strictly shrinks. For the upper bound (first index with `a[i] > target`) change `<` to `<=`. In fixed-width languages compute the midpoint as `lo + (hi - lo) / 2` (or an unsigned shift) because `(lo + hi) / 2` overflows when both exceed half the integer range.

#### Binary search — Python

```python
def lower_bound(a, target):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

#### Binary search — JavaScript

```javascript
function lowerBound(a, target) {
  let lo = 0, hi = a.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (a[mid] < target) lo = mid + 1; else hi = mid;
  }
  return lo;
}
```

#### Binary search — TypeScript

```typescript
function lowerBound<T>(a: readonly T[], target: T, cmp: (x: T, y: T) => number): number {
  let lo = 0, hi = a.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (cmp(a[mid], target) < 0) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

lowerBound([1, 3, 3, 7], 3, (x, y) => x - y);   // 1
```

#### Binary search — Java

```java
static int lowerBound(int[] a, int target) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C#

```csharp
static int LowerBound(int[] a, int target) {
    int lo = 0, hi = a.Length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C

```c
#include <stddef.h>

size_t lower_bound(const int *a, size_t n, int target) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1; else hi = mid;
    }
    return lo;
}
```

#### Binary search — C++

```cpp
int lower_bound_index(const std::vector<int>& a, int target) {
    return int(std::lower_bound(a.begin(), a.end(), target) - a.begin());
}
```

#### Binary search — Go

```go
import (
	"cmp"
	"slices"
)

func lowerBound[T cmp.Ordered](a []T, target T) int {
	i, _ := slices.BinarySearch(a, target)   // earliest index with a[i] >= target
	return i
}

// Manual form with a predicate: sort.Search(len(a), func(i int) bool { return a[i] >= target })
```

#### Binary search — Rust

```rust
fn lower_bound(a: &[i32], target: i32) -> usize {
    a.partition_point(|&x| x < target)
}
```

#### Binary search — Ruby

```ruby
def lower_bound(a, target)
  a.bsearch_index { |x| x >= target } || a.size
end
```

### Binary search variants and binary search on the answer

Meta: category=algorithm | topic=binary-search-variants | languages=all | tags=rotated-array, peak-element, search-on-answer, monotonic-predicate, 2d-matrix | time=O(log n) or O(log(range) × check cost)

Binary search works on any monotonic predicate, not only sorted arrays: if `feasible(v)` is false up to some point and true after, binary search finds the boundary.

| Problem | Approach |
| --- | --- |
| First and last occurrence | Lower bound of x; upper bound of x minus 1 |
| Search in rotated sorted array | Compare `a[mid]` with `a[hi]` to find the sorted half, then check whether the target lies inside it |
| Find minimum in rotated array | If `a[mid] > a[hi]` go right, else left (including mid) |
| Peak element | If `a[mid] < a[mid + 1]` go right, else left |
| Search a row-major sorted matrix | Treat it as a flat array: row = mid ÷ cols, col = mid mod cols |
| Binary search on the answer | Find the smallest v with `feasible(v)`: ship capacity within D days, Koko eating bananas, split array largest sum, minimum days to make bouquets |
| Real-valued answers | Loop a fixed \~100 iterations instead of comparing with an epsilon |

#### Binary search on the answer — Python

```python
def min_feasible(lo, hi, feasible):    # smallest v in [lo, hi] with feasible(v) true
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

# Example: minimum ship capacity to deliver weights within `days`
def ship_within_days(weights, days):
    def feasible(cap):
        need, load = 1, 0
        for w in weights:
            if load + w > cap:
                need, load = need + 1, 0
            load += w
        return need <= days
    return min_feasible(max(weights), sum(weights), feasible)
```

### Two pointers

Meta: category=algorithm | topic=two-pointers | languages=all | tags=sorted-array, pair-sum, three-sum, in-place, palindrome | time=O(n), O(n²) for 3-sum | space=O(1)

Two indices move through the data according to a rule, replacing a nested loop. Opposite-direction pointers solve pair sum in a sorted array, container with most water, valid palindrome and trapping rain water. Same-direction (fast and slow) pointers solve removing duplicates in place, moving zeros, and linked-list cycle and middle detection. 3-sum sorts the array, fixes one element and runs opposite pointers on the rest.

#### Pair sum in a sorted array — Python

```python
def pair_sum_sorted(a, target):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return i, j
        if s < target:
            i += 1
        else:
            j -= 1
    return None
```

### Sliding window

Meta: category=algorithm | topic=sliding-window | languages=all | tags=subarray, substring, variable-window, fixed-window, frequency-map | time=O(n) | space=O(alphabet) or O(k)

A sliding window keeps a contiguous range \[left, right\]. The right edge advances every step; the left edge advances while the window violates the constraint. Each index enters and leaves once, so the scan is O(n). Fixed-size windows compute rolling sums or averages; variable windows solve longest substring without repeats, minimum window substring, longest subarray with at most k distinct values, and minimum-size subarray sum. Sliding windows need non-negative values for sum constraints; with negatives, use prefix sums with a hash map.

#### Longest substring without repeating characters — Python

```python
def longest_unique_substring(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```

### Prefix sums and difference arrays

Meta: category=algorithm | topic=prefix-sums | languages=all | tags=prefix-sum, range-sum, 2d-prefix-sum, difference-array, cumulative-sum, product-except-self | time=O(n) build, O(1) per range query | space=O(n)

A prefix sum array stores `pre[i]` = sum of the first i elements (with `pre[0] = 0`), so any range sum is `pre[r + 1] - pre[l]` in O(1) after an O(n) build. The 2D version answers rectangle sums in O(1) by inclusion–exclusion. A difference array is the inverse: adding `delta` to every element in \[l, r\] becomes two O(1) writes (`diff[l] += delta`, `diff[r + 1] -= delta`), and one prefix-sum pass rebuilds the final array. Prefix sums combined with a hash map count subarrays with a target sum even when values are negative (see the hash table patterns chunk). Prefix and suffix products solve "product of array except self" without division. Use a Fenwick or segment tree instead when values change between queries.

#### Prefix sums, 2D prefix sums and difference array — Python

```python
from itertools import accumulate

def prefix_sums(nums):
    return [0, *accumulate(nums)]            # pre[i] = sum(nums[:i])

def range_sum(pre, l, r):                     # sum of nums[l..r], inclusive
    return pre[r + 1] - pre[l]

def prefix_2d(grid):
    rows, cols = len(grid), len(grid[0])
    P = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            P[r + 1][c + 1] = grid[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
    return P

def rect_sum(P, r1, c1, r2, c2):              # inclusive corners (r1, c1) to (r2, c2)
    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]

def apply_range_adds(n, updates):             # updates = [(l, r, delta)], inclusive
    diff = [0] * (n + 1)
    for l, r, delta in updates:
        diff[l] += delta
        diff[r + 1] -= delta
    return list(accumulate(diff[:n]))
```

### Graph algorithm selection guide

Meta: category=algorithm | topic=graph-algorithm-selection | languages=all | tags=shortest-path, mst, topological-sort, scc, max-flow, bipartite

Pick a graph algorithm by the question asked and the edge weights allowed.

| Problem | Algorithm | Time | Constraint |
| --- | --- | --- | --- |
| Shortest path, unweighted | BFS | O(V + E) | — |
| Shortest path, weights 0 or 1 | 0-1 BFS with a deque | O(V + E) | Weights 0 or 1 only |
| Shortest path, non-negative weights | Dijkstra | O((V + E) log V) | No negative edges |
| Shortest path, negative weights | Bellman-Ford (SPFA variant) | O(VE) | Detects negative cycles |
| All-pairs shortest paths | Floyd-Warshall | O(V³) | V up to \~500 |
| Shortest path with a heuristic | A\* | Depends on heuristic | Heuristic must never overestimate |
| Order tasks with dependencies | Topological sort (Kahn or DFS) | O(V + E) | Directed acyclic graph |
| Minimum spanning tree | Kruskal / Prim | O(E log E) / O(E log V) | Undirected, connected |
| Strongly connected components | Tarjan / Kosaraju | O(V + E) | Directed |
| Bridges and articulation points | Tarjan low-link | O(V + E) | Undirected |
| Maximum flow, minimum cut | Edmonds-Karp / Dinic | O(VE²) / O(V²E) | Capacities on edges |
| Two-colouring, bipartite check | BFS or DFS colouring | O(V + E) | — |

### Breadth-first search (BFS)

Meta: category=algorithm | topic=bfs | languages=all | tags=graph, traversal, shortest-path-unweighted, queue, level-order, grid | time=O(V + E) | space=O(V)

BFS explores vertices in order of distance from the source using a FIFO queue, so the first time a vertex is reached is along a shortest path in an unweighted graph. Mark vertices as visited when they are enqueued, not when dequeued, or they may be enqueued many times. Uses: shortest path in a maze or grid, word ladder, rotting oranges, minimum knight moves, level-order traversal, bipartite checking. Multi-source BFS starts with every source in the queue at distance 0.

#### BFS — Python

```python
from collections import deque

def bfs(adj, src):
    dist = [-1] * len(adj)
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

#### BFS — JavaScript

```javascript
function bfs(adj, src) {
  const dist = new Array(adj.length).fill(-1);
  dist[src] = 0;
  const q = [src];
  for (let head = 0; head < q.length; head++) {      // head index keeps dequeue O(1)
    const u = q[head];
    for (const v of adj[u]) if (dist[v] === -1) { dist[v] = dist[u] + 1; q.push(v); }
  }
  return dist;
}
```

#### BFS — TypeScript

```typescript
function bfs(adj: readonly (readonly number[])[], src: number): number[] {
  const dist: number[] = new Array<number>(adj.length).fill(-1);
  dist[src] = 0;
  const queue: number[] = [src];
  for (let head = 0; head < queue.length; head++) {   // head index keeps dequeue O(1)
    const u = queue[head];
    for (const v of adj[u]) {
      if (dist[v] === -1) {
        dist[v] = dist[u] + 1;
        queue.push(v);
      }
    }
  }
  return dist;
}
```

#### BFS — Java

```java
static int[] bfs(List<List<Integer>> adj, int src) {
    int[] dist = new int[adj.size()];
    Arrays.fill(dist, -1);
    dist[src] = 0;
    ArrayDeque<Integer> q = new ArrayDeque<>();
    q.add(src);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : adj.get(u)) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }
    }
    return dist;
}
```

#### BFS — C#

```csharp
static int[] Bfs(List<int>[] adj, int src) {
    var dist = new int[adj.Length];
    Array.Fill(dist, -1);
    dist[src] = 0;
    var q = new Queue<int>();
    q.Enqueue(src);
    while (q.Count > 0) {
        int u = q.Dequeue();
        foreach (int v in adj[u])
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q.Enqueue(v); }
    }
    return dist;
}
```

#### BFS — C

```c
#include <stdlib.h>

/* Graph in CSR form: neighbours of u are nbr[off[u] .. off[u + 1]) */
void bfs(int n, const int *off, const int *nbr, int src, int *dist) {
    int *q = malloc(n * sizeof *q), head = 0, tail = 0;
    for (int i = 0; i < n; i++) dist[i] = -1;
    dist[src] = 0; q[tail++] = src;
    while (head < tail) {
        int u = q[head++];
        for (int k = off[u]; k < off[u + 1]; k++) {
            int v = nbr[k];
            if (dist[v] == -1) { dist[v] = dist[u] + 1; q[tail++] = v; }
        }
    }
    free(q);
}
```

#### BFS — C++

```cpp
std::vector<int> bfs(const std::vector<std::vector<int>>& adj, int src) {
    std::vector<int> dist(adj.size(), -1);
    dist[src] = 0;
    std::queue<int> q;
    q.push(src);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (dist[v] == -1) { dist[v] = dist[u] + 1; q.push(v); }
    }
    return dist;
}
```

#### BFS — Go

```go
func bfs(adj [][]int, src int) []int {
	dist := make([]int, len(adj))
	for i := range dist {
		dist[i] = -1
	}
	dist[src] = 0
	queue := []int{src}
	for head := 0; head < len(queue); head++ {
		u := queue[head]
		for _, v := range adj[u] {
			if dist[v] == -1 {
				dist[v] = dist[u] + 1
				queue = append(queue, v)
			}
		}
	}
	return dist
}
```

#### BFS — Rust

```rust
use std::collections::VecDeque;

fn bfs(adj: &[Vec<usize>], src: usize) -> Vec<Option<usize>> {
    let mut dist = vec![None; adj.len()];
    dist[src] = Some(0);
    let mut q = VecDeque::from([src]);
    while let Some(u) = q.pop_front() {
        let d = dist[u].unwrap();
        for &v in &adj[u] {
            if dist[v].is_none() { dist[v] = Some(d + 1); q.push_back(v); }
        }
    }
    dist
}
```

#### BFS — Ruby

```ruby
def bfs(adj, src)
  dist = Array.new(adj.size, -1)
  dist[src] = 0
  queue = [src]
  until queue.empty?
    u = queue.shift                     # O(1) amortised in CRuby
    adj[u].each do |v|
      next unless dist[v] == -1
      dist[v] = dist[u] + 1
      queue << v
    end
  end
  dist
end
```

### Dijkstra's shortest path

Meta: category=algorithm | topic=dijkstra | languages=all | tags=graph, shortest-path, weighted, priority-queue, non-negative-weights | time=O((V + E) log V) with a binary heap | space=O(V + E)

Dijkstra repeatedly takes the unsettled vertex with the smallest tentative distance from a min-heap and relaxes its outgoing edges (if `dist[u] + w < dist[v]`, update `dist[v]` and push it). Instead of a decrease-key operation, push duplicates and skip any popped entry whose distance is stale. It is correct only for non-negative weights; use Bellman-Ford when edges can be negative. Store a `prev[v]` array while relaxing to reconstruct the path. For dense graphs, an O(V²) array scan without a heap is faster. Uses: network delay time, cheapest flights (with a stop-count state), path with minimum effort on a grid.

#### Dijkstra — Python

```python
import heapq

def dijkstra(adj, src):                 # adj[u] = [(v, w), ...]
    dist = [float("inf")] * len(adj)
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue                    # stale entry
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist
```

#### Dijkstra — JavaScript

```javascript
// Requires the Heap class from the "Binary heap — JavaScript" chunk.
function dijkstra(adj, src) {               // adj[u] = [[v, w], ...]
  const dist = new Array(adj.length).fill(Infinity);
  dist[src] = 0;
  const pq = new Heap((a, b) => a[0] - b[0]);
  pq.push([0, src]);
  while (pq.size) {
    const [d, u] = pq.pop();
    if (d > dist[u]) continue;
    for (const [v, w] of adj[u]) if (d + w < dist[v]) { dist[v] = d + w; pq.push([dist[v], v]); }
  }
  return dist;
}
```

#### Dijkstra — TypeScript

```typescript
// Requires the Heap<T> class from the "Binary heap — TypeScript" chunk.
type Edge = readonly [to: number, weight: number];

function dijkstra(adj: readonly (readonly Edge[])[], src: number): number[] {
  const dist: number[] = new Array<number>(adj.length).fill(Infinity);
  dist[src] = 0;
  const pq = new Heap<[number, number]>((x, y) => x[0] - y[0]);   // [distance, vertex]
  pq.push([0, src]);
  while (pq.size > 0) {
    const [d, u] = pq.pop()!;
    if (d > dist[u]) continue;                                    // stale entry
    for (const [v, w] of adj[u]) {
      if (d + w < dist[v]) {
        dist[v] = d + w;
        pq.push([dist[v], v]);
      }
    }
  }
  return dist;
}
```

#### Dijkstra — Java

```java
static long[] dijkstra(List<List<int[]>> adj, int src) {   // edge = {v, w}
    long[] dist = new long[adj.size()];
    Arrays.fill(dist, Long.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
    pq.add(new long[]{0, src});
    while (!pq.isEmpty()) {
        long[] top = pq.poll();
        long d = top[0]; int u = (int) top[1];
        if (d > dist[u]) continue;
        for (int[] e : adj.get(u))
            if (d + e[1] < dist[e[0]]) { dist[e[0]] = d + e[1]; pq.add(new long[]{dist[e[0]], e[0]}); }
    }
    return dist;
}
```

#### Dijkstra — C#

```csharp
static long[] Dijkstra(List<(int to, int w)>[] adj, int src) {
    var dist = new long[adj.Length];
    Array.Fill(dist, long.MaxValue);
    dist[src] = 0;
    var pq = new PriorityQueue<int, long>();
    pq.Enqueue(src, 0);
    while (pq.TryDequeue(out int u, out long d)) {
        if (d > dist[u]) continue;
        foreach (var (v, w) in adj[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.Enqueue(v, dist[v]); }
    }
    return dist;
}
```

#### Dijkstra — C

```c
#include <limits.h>
#include <stdlib.h>

/* Dense O(V^2) version: w[u * n + v] < 0 means no edge. Best when E is close to V^2. */
void dijkstra(int n, const int *w, int src, long long *dist) {
    char *done = calloc(n, 1);
    for (int i = 0; i < n; i++) dist[i] = LLONG_MAX;
    dist[src] = 0;
    for (int it = 0; it < n; it++) {
        int u = -1;
        for (int i = 0; i < n; i++)
            if (!done[i] && (u == -1 || dist[i] < dist[u])) u = i;
        if (dist[u] == LLONG_MAX) break;
        done[u] = 1;
        for (int v = 0; v < n; v++)
            if (w[u * n + v] >= 0 && dist[u] + w[u * n + v] < dist[v]) dist[v] = dist[u] + w[u * n + v];
    }
    free(done);
}
```

#### Dijkstra — C++

```cpp
std::vector<long long> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& adj, int src) {
    std::vector<long long> dist(adj.size(), LLONG_MAX);
    dist[src] = 0;
    using P = std::pair<long long, int>;
    std::priority_queue<P, std::vector<P>, std::greater<P>> pq;
    pq.push({0, src});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [v, w] : adj[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
    }
    return dist;
}
```

#### Dijkstra — Go

```go
import (
	"container/heap"
	"math"
)

type Edge struct{ to, w int }
type entry struct{ d, u int }
type distHeap []entry

func (h distHeap) Len() int           { return len(h) }
func (h distHeap) Less(i, j int) bool { return h[i].d < h[j].d }
func (h distHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *distHeap) Push(x any)        { *h = append(*h, x.(entry)) }
func (h *distHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

func dijkstra(adj [][]Edge, src int) []int {
	dist := make([]int, len(adj))
	for i := range dist {
		dist[i] = math.MaxInt
	}
	dist[src] = 0
	h := &distHeap{{0, src}}                // a one-element slice is already a valid heap
	for h.Len() > 0 {
		cur := heap.Pop(h).(entry)
		if cur.d > dist[cur.u] {
			continue                           // stale entry
		}
		for _, e := range adj[cur.u] {
			if nd := cur.d + e.w; nd < dist[e.to] {
				dist[e.to] = nd
				heap.Push(h, entry{nd, e.to})
			}
		}
	}
	return dist
}
```

#### Dijkstra — Rust

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

fn dijkstra(adj: &[Vec<(usize, u64)>], src: usize) -> Vec<u64> {
    let mut dist = vec![u64::MAX; adj.len()];
    dist[src] = 0;
    let mut pq = BinaryHeap::from([Reverse((0u64, src))]);
    while let Some(Reverse((d, u))) = pq.pop() {
        if d > dist[u] { continue; }
        for &(v, w) in &adj[u] {
            let nd = d + w;
            if nd < dist[v] { dist[v] = nd; pq.push(Reverse((nd, v))); }
        }
    }
    dist
}
```

#### Dijkstra — Ruby

```ruby
# Requires the Heap class from the "Binary heap — Ruby" chunk.
def dijkstra(adj, src)                  # adj[u] = [[v, w], ...]
  dist = Array.new(adj.size, Float::INFINITY)
  dist[src] = 0
  pq = Heap.new { |a, b| a[0] <=> b[0] }
  pq.push([0, src])
  while pq.size > 0
    d, u = pq.pop
    next if d > dist[u]
    adj[u].each do |v, w|
      next unless d + w < dist[v]
      dist[v] = d + w
      pq.push([dist[v], v])
    end
  end
  dist
end
```

### Depth-first search (DFS)

Meta: category=algorithm | topic=dfs | languages=all | tags=graph, traversal, stack, recursion, connected-components, cycle-detection, flood-fill | time=O(V + E) | space=O(V)

DFS follows one path as deep as possible before backtracking, using recursion or an explicit stack. It counts connected components and islands (flood fill), detects cycles (a back edge to a vertex still on the recursion stack in directed graphs, or to a non-parent visited vertex in undirected graphs), produces topological orders, and underlies Tarjan's SCC and bridge algorithms. Prefer the iterative form when depth can exceed the recursion limit.

#### Iterative DFS and island count — Python

```python
def dfs_order(adj, src):
    seen, stack, order = {src}, [src], []
    while stack:
        u = stack.pop()
        order.append(u)
        for v in reversed(adj[u]):
            if v not in seen:
                seen.add(v); stack.append(v)
    return order

def count_islands(grid):                # grid of "1" land and "0" water
    rows, cols, count = len(grid), len(grid[0]), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1":
                continue
            count += 1
            stack = [(r, c)]; grid[r][c] = "0"
            while stack:
                i, j = stack.pop()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == "1":
                        grid[ni][nj] = "0"; stack.append((ni, nj))
    return count
```

### Topological sort

Meta: category=algorithm | topic=topological-sort | languages=all | tags=dag, kahn, in-degree, dependency-order, course-schedule | time=O(V + E) | space=O(V)

A topological order lists every vertex of a directed acyclic graph before all vertices it points to. Kahn's algorithm repeatedly removes vertices with in-degree 0; if fewer than V vertices come out, the graph has a cycle. The DFS alternative appends each vertex after its descendants finish and reverses the result. Uses: course schedule, build order, task dependencies, alien dictionary.

#### Kahn's topological sort — Python

```python
from collections import deque

def topo_sort(n, edges):                # edges = [(u, v)] meaning u before v
    adj, indeg = [[] for _ in range(n)], [0] * n
    for u, v in edges:
        adj[u].append(v); indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None   # None = cycle
```

### Bellman-Ford

Meta: category=algorithm | topic=bellman-ford | languages=all | tags=graph, shortest-path, negative-weights, negative-cycle | time=O(VE) | space=O(V)

Bellman-Ford relaxes every edge V−1 times; a shortest path has at most V−1 edges, so distances are final afterwards. If any edge still relaxes in one more pass, a negative cycle is reachable. Limiting the passes to k+1 gives shortest paths using at most k+1 edges (cheapest flights within k stops) as long as each pass reads the previous pass's distances.

#### Bellman-Ford — Python

```python
def bellman_ford(n, edges, src):        # edges = [(u, v, w)]
    dist = [float("inf")] * n
    dist[src] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; changed = True
        if not changed:
            break
    if any(dist[u] + w < dist[v] for u, v, w in edges):
        raise ValueError("negative cycle reachable from source")
    return dist
```

### Floyd-Warshall

Meta: category=algorithm | topic=floyd-warshall | languages=all | tags=graph, all-pairs-shortest-path, dynamic-programming, transitive-closure | time=O(V³) | space=O(V²)

Floyd-Warshall computes shortest paths between every pair of vertices by allowing each vertex k in turn as an intermediate: `d[i][j] = min(d[i][j], d[i][k] + d[k][j])`. The k loop must be outermost. A negative value on the diagonal afterwards signals a negative cycle. Replacing min/plus with or/and gives transitive closure (reachability).

#### Floyd-Warshall — Python

```python
def floyd_warshall(d):                  # d = V×V matrix; inf = no edge; 0 on the diagonal
    n = len(d)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == float("inf"):
                continue
            row = d[i]
            for j in range(n):
                if dik + dk[j] < row[j]:
                    row[j] = dik + dk[j]
    return d
```

### Minimum spanning tree (Kruskal and Prim)

Meta: category=algorithm | topic=minimum-spanning-tree | languages=all | tags=graph, mst, kruskal, prim, union-find, greedy | time=Kruskal O(E log E); Prim O(E log V) | space=O(V + E)

A minimum spanning tree connects all vertices of an undirected weighted graph with the least total edge weight. Kruskal sorts edges by weight and adds each edge that joins two different components, tracked with union-find. Prim grows one tree from a start vertex, repeatedly adding the cheapest edge leaving the tree via a min-heap; it suits dense graphs and adjacency lists. Both are greedy and correct by the cut property. Uses: min cost to connect points, network design, clustering.

#### Kruskal's MST — Python

```python
def kruskal(n, edges):                  # edges = [(u, v, w)]
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    total, mst = 0, []
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w; mst.append((u, v, w))
    return total, mst                   # len(mst) < n - 1 means the graph is disconnected
```

### Strongly connected components (Tarjan)

Meta: category=algorithm | topic=strongly-connected-components | languages=all | tags=graph, scc, tarjan, kosaraju, low-link, directed | time=O(V + E) | space=O(V)

A strongly connected component is a maximal set of vertices where each can reach every other. Tarjan's algorithm runs one DFS, giving each vertex a discovery index and a low-link value (the smallest index reachable through its subtree and one back edge); when a vertex's low-link equals its own index, it roots a component, which is popped from the stack. Kosaraju's alternative runs DFS twice, once on the reversed graph. Condensing SCCs yields a DAG. The same low-link idea finds bridges and articulation points in undirected graphs.

#### Tarjan's SCC — Python

```python
import sys

def tarjan_scc(adj):
    sys.setrecursionlimit(max(10_000, 2 * len(adj) + 10))
    n, counter = len(adj), [0]
    index, low = [-1] * n, [0] * n
    on_stack, stack, comps = [False] * n, [], []

    def strong(u):
        index[u] = low[u] = counter[0]; counter[0] += 1
        stack.append(u); on_stack[u] = True
        for v in adj[u]:
            if index[v] == -1:
                strong(v); low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], index[v])
        if low[u] == index[u]:
            comp = []
            while True:
                w = stack.pop(); on_stack[w] = False; comp.append(w)
                if w == u:
                    break
            comps.append(comp)

    for u in range(n):
        if index[u] == -1:
            strong(u)
    return comps
```

## Algorithm paradigms

Each chunk covers one problem-solving strategy: when it applies, how to structure it, and the classic problems it solves.

### Dynamic programming framework

Meta: category=paradigm | topic=dynamic-programming | languages=all | tags=dp, memoisation, tabulation, overlapping-subproblems, optimal-substructure

Dynamic programming applies when a problem has overlapping subproblems and optimal substructure (the best answer is built from best answers to smaller subproblems). Define four things: the state (what `dp[i]` or `dp[i][j]` means), the transition (how a state is computed from smaller ones), the base cases, and the evaluation order. Top-down memoisation is quickest to write; bottom-up tabulation avoids recursion limits and allows keeping only the previous row, cutting space from O(nm) to O(m).

| Pattern | State | Classic problems | Time |
| --- | --- | --- | --- |
| 1D linear | best for prefix i | Climbing stairs, house robber, decode ways, word break | O(n) |
| Maximum subarray | best sum ending at i | Kadane, maximum product subarray | O(n) |
| 0/1 knapsack | best for capacity w using items so far | Subset sum, partition equal subset sum, target sum | O(nW) |
| Unbounded knapsack | best for amount a | Coin change (fewest coins, number of ways) | O(n·amount) |
| Two sequences | answer for prefixes i and j | Longest common subsequence, edit distance, interleaving string | O(nm) |
| Increasing subsequence | smallest tail per length | Longest increasing subsequence, Russian doll envelopes | O(n log n) |
| Grid | best for cell (r, c) | Unique paths, minimum path sum, maximal square | O(RC) |
| Interval | answer for range \[i, j\] | Matrix-chain multiplication, burst balloons, palindrome partitioning | O(n³) |
| Bitmask | best for visited set and last node | Travelling salesman, assignment | O(2ⁿ·n²) |
| Tree | values returned from children | House robber III, tree diameter, binary tree maximum path sum | O(n) |
| State machine | best at day i in state s | Stock buy/sell with cooldown or fees | O(n) |
| Digit | (position, tight, state) | Count numbers ≤ N with a digit property | O(digits × states) |

Memoisation per language: Python `@functools.cache`; JavaScript and TypeScript a `Map` or typed array; Java and C# a `HashMap` / `Dictionary` or an array filled with a sentinel; C a static array initialised to a sentinel; C++ a `std::vector` or `std::unordered_map`; Go a `map` or a slice filled with a sentinel, used by a recursive closure declared as `var dfs func(int) int`; Rust a `Vec<Option<T>>` passed as `&mut`; Ruby a `Hash` (`@memo[key] ||= compute`, which recomputes if the stored value is `nil` or `false`).

### Knapsack and coin change

Meta: category=paradigm | topic=knapsack-coin-change | languages=all | tags=dp, 0-1-knapsack, unbounded-knapsack, subset-sum, coin-change | time=O(n × capacity) | space=O(capacity)

In 0/1 knapsack each item is used at most once, so the 1D table is filled with capacity decreasing (each item reads values from before it was considered). In unbounded knapsack and coin change, items repeat, so capacity increases. For counting combinations in coin change, loop coins outside and amounts inside; swapping the loops counts ordered permutations instead.

#### Knapsack and coin change — Python

```python
def knapsack_01(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):      # decreasing: each item once
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]

def coin_change_min(coins, amount):             # fewest coins, -1 if impossible
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] <= amount else -1

def coin_change_ways(coins, amount):            # number of combinations
    dp = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]
```

### Two-sequence DP: edit distance and longest common subsequence

Meta: category=paradigm | topic=sequence-dp | languages=all | tags=dp, edit-distance, levenshtein, lcs, string-alignment | time=O(nm) | space=O(min(n, m)) with rolling rows

`dp[i][j]` answers the question for the first i characters of a and the first j of b. Edit distance takes the diagonal for a match, else 1 plus the minimum of insert, delete and replace. LCS takes the diagonal plus 1 on a match, else the larger of dropping a character from either side. Only the previous row is needed, so space shrinks to one row.

#### Edit distance and LCS — Python

```python
def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = prev[j - 1] if ca == cb else 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[-1]

def lcs_length(a, b):
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0] * (len(b) + 1)
        for j, cb in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]
```

### Longest increasing subsequence

Meta: category=paradigm | topic=longest-increasing-subsequence | languages=all | tags=dp, lis, patience-sorting, binary-search | time=O(n log n) | space=O(n)

The O(n²) DP sets `dp[i]` to 1 plus the best `dp[j]` over earlier smaller values. The O(n log n) method keeps `tails[k]`, the smallest possible tail of an increasing subsequence of length k+1; each element replaces the first tail ≥ it (lower bound), or extends the list. The final list length is the LIS length (the list itself is not necessarily a valid subsequence). Use upper bound instead for non-decreasing subsequences.

#### Longest increasing subsequence — Python

```python
from bisect import bisect_left

def lis_length(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

### Kadane's maximum subarray

Meta: category=paradigm | topic=kadane | languages=all | tags=dp, maximum-subarray, greedy, contiguous | time=O(n) | space=O(1)

Kadane's algorithm tracks the best sum of a subarray ending at the current index: either extend the previous subarray or start fresh at the current element. The global maximum of those values is the answer. For maximum product, track both the maximum and minimum ending here, since a negative number swaps them. For a circular array, the answer is the larger of the normal maximum and total sum minus the minimum subarray (unless all values are negative).

#### Kadane's algorithm — Python

```python
def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

### Greedy algorithms

Meta: category=paradigm | topic=greedy | languages=all | tags=greedy, exchange-argument, intervals, scheduling, huffman | time=usually O(n log n) for the sort

A greedy algorithm commits to the locally best choice at each step and never revisits it. It is correct only when an exchange argument shows that replacing any optimal solution's choice with the greedy choice never makes it worse; otherwise use dynamic programming.

| Problem | Greedy rule |
| --- | --- |
| Activity selection, non-overlapping intervals | Sort by end time; take each interval starting at or after the last taken end |
| Merge intervals | Sort by start; extend the current interval while the next one overlaps |
| Minimum arrows / meeting rooms | Sort by end (arrows) or sweep start and end times with a min-heap (rooms) |
| Jump game | Track the farthest reachable index |
| Gas station | If total gas ≥ total cost, start after the last index where the running balance went negative |
| Task scheduler | Place the most frequent task first; fill gaps with other tasks or idle slots |
| Huffman coding | Repeatedly merge the two lowest-frequency nodes from a min-heap |
| Fractional knapsack | Take items in decreasing value-to-weight ratio |
| Coin change | Greedy works only for canonical coin systems such as 1, 5, 10, 25; use DP otherwise |

#### Merge intervals — Python

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

### Backtracking

Meta: category=paradigm | topic=backtracking | languages=all | tags=recursion, permutations, subsets, combinations, n-queens, sudoku, pruning | time=exponential: O(2ⁿ) subsets, O(n!) permutations

Backtracking builds a candidate one choice at a time, recurses, then undoes the choice before trying the next. Pruning cuts branches that cannot lead to a valid answer (a running sum over target, a queen under attack). Template: if the candidate is complete, record a copy; otherwise, for each valid choice, choose, recurse, un-choose. To skip duplicate results from repeated values, sort first and skip a value equal to its predecessor at the same depth. Problems: subsets, permutations, combinations, combination sum, N-Queens, Sudoku solver, word search, palindrome partitioning, generate parentheses.

#### Subsets, permutations and N-Queens — Python

```python
def subsets(nums):
    res, path = [], []
    def go(start):
        res.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return res

def permutations(nums):
    res, path, used = [], [], [False] * len(nums)
    def go():
        if len(path) == len(nums):
            res.append(path[:]); return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True; path.append(x)
            go()
            path.pop(); used[i] = False
    go()
    return res

def n_queens(n):
    cols, diag1, diag2, board, res = set(), set(), set(), [], []
    def place(r):
        if r == n:
            res.append(["." * c + "Q" + "." * (n - c - 1) for c in board]); return
        for c in range(n):
            if c in cols or r - c in diag1 or r + c in diag2:
                continue
            cols.add(c); diag1.add(r - c); diag2.add(r + c); board.append(c)
            place(r + 1)
            cols.remove(c); diag1.remove(r - c); diag2.remove(r + c); board.pop()
    place(0)
    return res
```

### Divide and conquer

Meta: category=paradigm | topic=divide-and-conquer | languages=all | tags=recursion, master-theorem, merge-sort, karatsuba, closest-pair

Divide and conquer splits a problem into independent subproblems, solves each recursively, and combines the results. Unlike dynamic programming, the subproblems do not overlap, so no memoisation is needed. For a recurrence T(n) = a·T(n/b) + f(n), with a subproblems of size n/b and combine cost f(n), the master theorem gives:

```latex
T(n)=\begin{cases}\Theta(n^{\log_b a}) & f(n)=O(n^{\log_b a-\epsilon})\\ \Theta(n^{\log_b a}\log n) & f(n)=\Theta(n^{\log_b a})\\ \Theta(f(n)) & f(n)=\Omega(n^{\log_b a+\epsilon})\end{cases}
```

Examples: merge sort (a = 2, b = 2, f = n → O(n log n)), binary search (a = 1, b = 2, f = 1 → O(log n)), fast exponentiation (O(log n)), Karatsuba multiplication (O(n^1.585)), Strassen matrix multiplication (O(n^2.81)), closest pair of points (O(n log n)), and counting inversions during merge sort.

## Strings, math and bit manipulation

Each chunk covers one family of techniques that recur across DSA problems regardless of language.

### String pattern matching

Meta: category=algorithm | topic=string-matching | languages=all | tags=kmp, rabin-karp, z-algorithm, aho-corasick, manacher, suffix-array, substring-search | time=O(n + k) for KMP and Z

Naive matching tries every alignment in O(nk) for text length n and pattern length k. Linear-time algorithms avoid re-reading text characters.

| Algorithm | Time | Idea | Use when |
| --- | --- | --- | --- |
| KMP | O(n + k) | Failure function: longest proper prefix of the pattern that is also a suffix at each position | Single pattern, guaranteed linear time |
| Z-algorithm | O(n + k) | Z\[i\] = length of the longest prefix match starting at i; run on `pattern + "$" + text` | Single pattern, prefix-based problems |
| Rabin–Karp | O(n + k) average | Rolling polynomial hash, verify on a hash match | Many patterns of one length, duplicate substrings |
| Aho–Corasick | O(n + total pattern length + matches) | Trie of patterns with failure links | Many patterns at once |
| Manacher | O(n) | Reuses mirror palindrome radii | Longest palindromic substring |
| Suffix array + LCP | O(n log n) build | Sorted suffixes with longest common prefixes | Distinct substrings, longest repeated substring |

Built-in substring search (fine for most problems): Python `str.find`, JavaScript and TypeScript `indexOf`, Java `indexOf`, C# `IndexOf(s, StringComparison.Ordinal)`, C `strstr`, C++ `std::string::find` or `std::boyer_moore_searcher`, Go `strings.Index`, Rust `str::find`, Ruby `String#index`.

#### KMP search — Python

```python
def kmp_search(text, pat):
    fail, k = [0] * len(pat), 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]:
            k = fail[k - 1]
        if pat[i] == pat[k]:
            k += 1
        fail[i] = k
    matches, k = [], 0
    for i, ch in enumerate(text):
        while k and ch != pat[k]:
            k = fail[k - 1]
        if ch == pat[k]:
            k += 1
        if k == len(pat):
            matches.append(i - k + 1)
            k = fail[k - 1]
    return matches
```

#### Rabin–Karp search — Python

```python
def rabin_karp(text, pat, base=131, mod=(1 << 61) - 1):
    n, k = len(text), len(pat)
    if k > n:
        return []
    hp = ht = 0
    power = pow(base, k - 1, mod)
    for i in range(k):
        hp = (hp * base + ord(pat[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    matches = []
    for i in range(n - k + 1):
        if hp == ht and text[i:i + k] == pat:
            matches.append(i)
        if i + k < n:
            ht = ((ht - ord(text[i]) * power) * base + ord(text[i + k])) % mod
    return matches
```

### Number theory essentials

Meta: category=algorithm | topic=number-theory | languages=all | tags=gcd, lcm, modular-exponentiation, sieve, modular-inverse, combinations, primes | time=gcd O(log min(a, b)); mod pow O(log e); sieve O(n log log n)

- **GCD and LCM:** Euclid's algorithm replaces (a, b) with (b, a mod b) until b = 0. LCM = a ÷ gcd(a, b) × b (divide first to avoid overflow).
- **Fast modular exponentiation:** square the base and halve the exponent each step, multiplying the result in when the low bit is 1.
- **Sieve of Eratosthenes:** mark multiples of each prime from p² upward; all primes up to n in O(n log log n).
- **Modular inverse:** for prime p, a⁻¹ ≡ a^(p−2) mod p (Fermat); for general moduli use the extended Euclidean algorithm.
- **Combinations mod p:** precompute factorials and inverse factorials for O(1) queries, or multiply and invert once per query.
- **Common modulus:** 10⁹ + 7 is prime, and the product of two residues fits in a signed 64-bit integer.
- **Primality:** trial division up to √n for single checks; Miller–Rabin for 64-bit values.

#### Number theory helpers — Python

```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_pow(base, exp, mod):
    result, base = 1, base % mod
    while exp:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result

def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = bytearray(len(is_prime[i * i::i]))
    return [i for i in range(n + 1) if is_prime[i]]

def ncr_mod(n, r, p=10**9 + 7):
    num = den = 1
    for i in range(r):
        num = num * (n - i) % p
        den = den * (i + 1) % p
    return num * pow(den, p - 2, p) % p       # Fermat inverse of den
```

### Bit manipulation techniques

Meta: category=algorithm | topic=bit-manipulation | languages=all | tags=bitmask, xor, lowest-set-bit, power-of-two, subset-enumeration | time=O(1) per operation

Integers double as sets of small indices: bit i set means element i is present, so union is `|`, intersection `&`, and difference `a & ~b`. Bitmask DP and subset enumeration rely on this for n up to about 20.

| Technique | Expression |
| --- | --- |
| Test bit i | `(x >> i) & 1` |
| Set, clear, toggle bit i | `x \| (1 << i)`, `x & ~(1 << i)`, `x ^ (1 << i)` |
| Lowest set bit | `x & -x` |
| Clear the lowest set bit | `x & (x - 1)` |
| Is a power of two | `x > 0 and (x & (x - 1)) == 0` |
| Count set bits by hand | Repeat `x &= x - 1` until zero (Kernighan) |
| Element appearing once when others appear twice | XOR of all elements |
| Missing number in 0..n | XOR of all indices and values |
| Enumerate all subsets of a mask | `s = mask; while s: ...; s = (s - 1) & mask` |
| All masks of n bits | `for mask in range(1 << n)` |

## Selection guide

### Choosing a data structure or technique

Meta: category=reference | topic=structure-selection | languages=all | tags=decision-guide, problem-patterns, interview

Match the operation a problem repeats most often to the structure or technique that makes it cheap.

| Problem signal | Reach for | Cost of the key operation |
| --- | --- | --- |
| Fast membership or duplicate check | Hash set | O(1) average |
| Key-to-value lookup, counting | Hash map | O(1) average |
| Sorted keys with floor, ceiling or range queries | Balanced search tree (sorted map) | O(log n) |
| Repeatedly extract the min or max, top-k | Binary heap | O(log n) |
| Process in arrival order, shortest path unweighted | Queue with BFS | O(1) per operation |
| Undo, nested structure, matching brackets | Stack | O(1) per operation |
| Next greater or smaller element, sliding-window max | Monotonic stack or deque | O(n) total |
| Prefix lookups on strings | Trie | O(k) per key |
| Range sum with point updates | Fenwick tree | O(log n) |
| Range min or max with updates | Segment tree | O(log n) |
| Merge groups, count components | Union-find | O(α(n)) |
| Evict the least recently used entry | Hash map + doubly linked list | O(1) |
| Approximate membership in little memory | Bloom filter | O(k) hashes |
| Sorted array, find a value or boundary | Binary search | O(log n) |
| Monotonic yes/no condition over an answer range | Binary search on the answer | O(log range × check) |
| Pair or triplet in a sorted array | Two pointers | O(n) or O(n²) |
| Longest or shortest contiguous subarray under a constraint | Sliding window | O(n) |
| Subarray sums with negative numbers | Prefix sums + hash map | O(n) |
| Weighted shortest path, non-negative weights | Dijkstra | O((V + E) log V) |
| Dependencies and ordering | Topological sort | O(V + E) |
| Optimal value with overlapping choices | Dynamic programming | Varies by state count |
| All combinations, permutations or placements | Backtracking | Exponential with pruning |
