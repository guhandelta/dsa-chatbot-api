---
track: algorithm
difficulty: Easy
algorithms: hash-keys
category: Data Structure
source: authored
io_mode: function
---
# Hash key requirements by language — Easy — Data Structure

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
