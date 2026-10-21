---
track: language
language: c
level: intermediate
order: 8
prerequisites: c-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: unique_count
starter_code: "#include <stddef.h>\n\nlong long unique_count(const long long* values, size_t n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# C: Sets and equality — Easy — Shared curriculum

## Learn
A set records membership: each distinct key is stored once, and adding a duplicate changes nothing. C has no standard set. When the keys are small integers from a known range, the simplest set is an array of flags indexed by the key (offset so that the smallest key maps to index 0); a larger or unbounded key space needs a hash table you build, or sorting followed by a scan. An index must always lie inside the array, so a key that can be negative must be shifted before it is used. A local array is not zeroed: write `= {0}` to start with every flag clear.

The contract here: `values` points to `n` integers (`n` is 0 to 1000), each between -1000 and 1000, and the function returns how many different values occur. Use a set; the order of the values does not matter.

## Common misconception
Using the value itself as the index fails for negative keys: `seen[-1]` is an access before the start of the array, which is undefined behaviour (and the remainder `key % size` of a negative key is also negative in C, because the sign follows the dividend). Map the range onto 0..size-1 first, for example `value + 1000` for keys from -1000 to 1000, which needs 2001 flags. Also count a value only the first time you see it; marking a flag that is already set must not increase the count. Do not fold negatives with `abs`, which would merge -5 and 5 into one flag, and check the extremes by hand: `{-5, 5}` has 2 distinct values and `{1000}` must land on the last index, 2000.

## Worked example
```c
bool present[16] = {false};
present[7] = true;
present[7] = true;
bool found = present[7];
```

`found` is true. Adding 7 twice sets the same flag twice, so there is still one member: membership is a property of the key, not a count of insertions. The flag array is the set; it works because every key is known to be in 0..15.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000. (In C a presence table over this key range is a set.)

## Example
Arguments: `[[]]` → `0` (the C call is `unique_count(values, 0)`)

## Starter code
```c
#include <stddef.h>

long long unique_count(const long long* values, size_t n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Create a zeroed flag table with one entry per possible value, shifted so that -1000 maps to index 0. For each element, check its flag: if it is clear, set it and increase the distinct count; if it is already set, do nothing.

## Solutions
### C
```c
#include <stddef.h>

long long unique_count(const long long* values, size_t n) {
    unsigned char seen[2001] = {0};
    long long distinct = 0;
    for (size_t i = 0; i < n; i++) {
        long long slot = values[i] + 1000;
        if (!seen[slot]) {
            seen[slot] = 1;
            distinct++;
        }
    }
    return distinct;
}
```
