---
track: language
language: c
level: expert
order: 12
prerequisites: c-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: has_pair
starter_code: "#include <stdbool.h>\n#include <stddef.h>\n\nbool has_pair(const long long* values, size_t n, long long target) {\n    // Write your solution here.\n    return false;\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# C: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how the work grows with the input size n; space complexity describes the extra storage. Two nested loops over all pairs do about n(n-1)/2 comparisons, which is O(n^2). A single pass that asks "have I already seen the partner of this element?" does O(n) lookups if a lookup takes constant time. In C you choose the lookup structure yourself: a hash table you build, or, when the keys come from a small known range, an array of flags indexed by the key (constant time per lookup, fixed extra space). An invariant states what is true before each iteration, for example "the table marks exactly the values at earlier indices".

The contract here: `values` points to `n` integers (`n` is 0 to 1000), and the elements and `target` are integers from -1000 to 1000. Return `true` when two elements at different indices sum to `target`. Note that `target - value` can leave the range -1000..1000, so check the range before using it as an index.

## Common misconception
Two different indices may hold the same value, but one index must not pair with itself: with `values = {1}` and `target = 2` the answer is false, even though 1 + 1 = 2. If you record the current element before you look for its partner, the element finds itself. Look up first, then record. A second C-specific trap: the partner `target - value` may be as low as -2000 or as high as 2000, outside a table that covers -1000..1000; indexing there is undefined behaviour. The target is an exact sum, not a lower bound, and the partner need not be the neighbour: by hand, `{1, 9, 8}` with target 9 is true (1 + 8, indices 0 and 2) while `{5, 6}` with target 9 is false (sum 11). The six tests do not distinguish an exact sum from "at least target" or a pair from adjacent elements only. A correct result on six tests is evidence, not proof; explain your invariant and complexity as part of the mastery check.

## Worked example
```c
size_t steps = 0;
for (size_t i = 0; i < 4; i++) {
    for (size_t j = i + 1; j < 4; j++) {
        steps++;
    }
}
```

`steps` is 6, which is 4 * 3 / 2: every pair is visited once. Doubling the number of elements roughly quadruples this count, whereas a single traversal that does one constant-time lookup per element grows only linearly. Count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set (here: a presence table over the key range) to practice one-pass reasoning. values has length n (0 to 1000); elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false` (the C call is `has_pair(values, 0, 2)`)

## Starter code
```c
#include <stdbool.h>
#include <stddef.h>

bool has_pair(const long long* values, size_t n, long long target) {
    // Write your solution here.
    return false;
}
```

## Approach
Keep a presence table for the values seen so far. For each element, compute the partner it needs; if the partner is inside the table's range and already marked, return `true`. Only afterwards mark the current element. Returning `false` after the loop covers empty and one-element arrays.

## Solutions
### C
```c
#include <stdbool.h>
#include <stddef.h>

bool has_pair(const long long* values, size_t n, long long target) {
    bool seen[2001] = {false};
    for (size_t i = 0; i < n; i++) {
        long long need = target - values[i];
        if (need >= -1000 && need <= 1000 && seen[need + 1000]) {
            return true;
        }
        seen[values[i] + 1000] = true;
    }
    return false;
}
```
