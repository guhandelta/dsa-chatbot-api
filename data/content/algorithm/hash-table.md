---
track: algorithm
difficulty: Easy
algorithms: hash-table
category: Data Structure
source: authored
io_mode: function
---
# Hash table — Easy — Data Structure

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
