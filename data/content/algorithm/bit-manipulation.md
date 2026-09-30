---
track: algorithm
difficulty: Medium
algorithms: bit-manipulation
category: Algorithm
source: authored
io_mode: function
---
# Bit manipulation techniques — Medium — Algorithm

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
