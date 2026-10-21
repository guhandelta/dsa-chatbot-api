---
track: language
language: c
level: intermediate
order: 6
prerequisites: c-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: count_above
starter_code: "#include <stddef.h>\n\nlong long count_above(const long long* values, size_t n, long long threshold) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# C: Arrays and lists — Easy — Shared curriculum

## Learn
An array stores elements of one type in consecutive memory, accessed by index from 0 to n - 1. In C an array that is passed to a function becomes a pointer to its first element, so the callee cannot tell how long it is: the convention, and the one the exercise runner uses, is a pointer plus a separate length (`const long long* values, size_t n`). `size_t` is unsigned, so `i < n` is the natural loop test. `const` on the pointed-to type promises that the function will not modify the caller's elements. Distinguish the index from the value stored at that index.

The contract here: `values` points to `n` elements, `n` is 0 to 1000, and the elements and `threshold` are integers from -1000 to 1000. The function returns how many elements are strictly greater than `threshold` and must not modify the array. When `n` is 0 the pointer must not be dereferenced.

## Common misconception
Inside the function `sizeof(values) / sizeof(values[0])` does not give the number of elements: `values` is a pointer, so `sizeof(values)` is the size of a pointer and the division yields 1 for 8-byte elements on a 64-bit platform (compilers warn with `-Wsizeof-pointer-div`). Use the `n` parameter. A loop written `i <= n` reads one element past the end, which is undefined behaviour. And "strictly greater" excludes elements equal to the threshold.

## Worked example
```c
long long scores[2] = {3, 8};
long long* alias = scores;
alias[0] = 5;
```

`scores[0]` is now 5 because `alias` points at the same storage; copying a pointer copies the address, not the elements. To keep the original values, copy the elements into a separate array (for example with a loop or `memcpy`) before changing them.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length n (0 to 1000); its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0` (the C call receives the array as a pointer and its length: `count_above(values, 0, 0)`)

## Starter code
```c
#include <stddef.h>

long long count_above(const long long* values, size_t n, long long threshold) {
    // Write your solution here.
    return 0;
}
```

## Approach
Traverse indices 0 to `n - 1` once, compare each element with `threshold` using `>`, and count the matches. Because the loop tests `i < n`, an empty array never touches the pointer.

## Solutions
### C
```c
#include <stddef.h>

long long count_above(const long long* values, size_t n, long long threshold) {
    long long count = 0;
    for (size_t i = 0; i < n; i++) {
        if (values[i] > threshold) {
            count++;
        }
    }
    return count;
}
```
