---
track: language
language: c
level: intermediate
order: 10
prerequisites: c-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: safe_at
starter_code: "#include <stddef.h>\n\nlong long safe_at(const long long* values, size_t n, long long index, long long fallback) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# C: Validation and failure contracts — Easy — Shared curriculum

## Learn
C does not check array bounds. Reading `values[index]` outside the array is undefined behaviour: it may crash, return garbage, or appear to work, and nothing throws. Validate the precondition before the access and define what invalid input means. Common failure contracts in C are a fallback value, a status code with an output parameter, or a `NULL` return; state which one you chose and what the function guarantees about its outputs on failure. This task chooses a fallback value.

A signed index and an unsigned length need care: when a signed and an unsigned operand of the same width meet in a comparison, the signed one is converted to unsigned, so a negative index silently becomes a huge number (`-1 < 1u` is false). Test the sign explicitly, then compare.

The contract here: `values` points to `n` elements (`n` is 0 to 100), all numeric inputs are integers from -1000 to 1000, and the function returns `values[index]` when the index is valid and `fallback` otherwise. Valid indices are 0 through `n - 1`.

## Common misconception
Index `n` is one past the end, not the last element: rejecting only when `index > n` (equivalently, accepting when `index <= n`) lets `index == n` through and reads outside the array. The valid range ends at `index < n`, and negative indices must be rejected separately. Do not rely on arithmetic accidents (a negative `long long` compared directly with a `size_t` is converted to unsigned and may happen to exceed `n`; `-Wextra` warns with `-Wsign-compare`); write the check so that its meaning is visible.

## Worked example
```c
bool parse_digit(char c, int* out) {
    if (c < '0' || c > '9') {
        return false;
    }
    *out = c - '0';
    return true;
}
```

`parse_digit('7', &d)` returns true and sets `d` to 7. `parse_digit('x', &d)` returns false and leaves `d` untouched, which is part of this function's contract: the caller must check the return value before using `d`. The exercise below deliberately chooses a fallback instead of a status code, so do not copy this contract into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length n (0 to 100); all numeric inputs are integers between -1000 and 1000. Do not read outside the array.

## Example
Arguments: `[[], 0, 9]` → `9` (the C call is `safe_at(values, 0, 0, 9)`)

## Starter code
```c
#include <stddef.h>

long long safe_at(const long long* values, size_t n, long long index, long long fallback) {
    // Write your solution here.
    return 0;
}
```

## Approach
Reject the index when it is negative or when it is not smaller than `n`, returning `fallback`; only then read the element. Do the negative test first so that the conversion to `size_t` is only applied to a nonnegative index. An empty array makes every index invalid.

## Solutions
### C
```c
#include <stddef.h>

long long safe_at(const long long* values, size_t n, long long index, long long fallback) {
    if (index < 0 || (size_t)index >= n) {
        return fallback;
    }
    return values[index];
}
```
