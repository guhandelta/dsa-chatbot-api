---
track: language
language: c
level: beginner
order: 4
prerequisites: c-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: distance
starter_code: "long long distance(long long a, long long b) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# C: Functions and contracts — Easy — Shared curriculum

## Learn
A C function has a return type, a name and a parameter list, and the compiler must have seen its declaration (a prototype or the definition) before a call. Arguments are passed by value: each parameter is a local copy, so assigning to a parameter never changes the caller's variable. Reaching the closing brace of a non-`void` function without a `return`, and then using the call's value, is undefined behaviour, so every path must return. Small functions with one purpose are easiest to verify.

The contract here: `a` and `b` are integers from -1000 to 1000 and the function returns their nonnegative distance as a `long long`. Keep the supplied name and argument order, because another program calls the function.

## Common misconception
Because arguments are copied, a function cannot hand a result back by modifying its parameter. With `void apply(long long a, long long c) { a += c; }` and a caller that runs `apply(total, 5);`, `total` is unchanged afterwards: only the function's own copy of `a` was updated. Results leave a function through `return` (or through a pointer that the caller passed in). A second trap here is the sign: the difference `a - b` is negative when `b` is larger, but a distance never is.

## Worked example
```c
long long twice(long long value) {
    return value * 2;
}

long long result = twice(4);
```

The argument 4 becomes the parameter `value` for this call, and the returned `result` is 8. A second call gets its own `value`. The exercise runner calls your function directly, so you do not write a `main`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return a `long long`.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```c
long long distance(long long a, long long b) {
    // Write your solution here.
    return 0;
}
```

## Approach
The distance is the difference of the larger and the smaller position, so decide which is larger and subtract in that order; alternatively compute the difference and discard its sign. Check the cases where `a > b`, `a < b` and `a == b`, and where both are negative.

## Solutions
### C
```c
long long distance(long long a, long long b) {
    long long diff = a - b;
    return diff < 0 ? -diff : diff;
}
```
