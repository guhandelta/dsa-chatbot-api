---
track: language
language: cpp
level: beginner
order: 4
prerequisites: cpp-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: distance_between
starter_code: "long long distance_between(long long a, long long b) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# C++: Functions and contracts — Easy — Shared curriculum

## Learn
A function contract names the parameter types, the return type and the valid inputs. Parameters are local variables initialized from the arguments; by default each one is a copy of the caller's value. `return` ends the call and hands a value back; printing does not satisfy a return-value contract. For a large read-only argument such as a vector, take it by `const` reference (`const std::vector<int>&`) so it is not copied. The exercise runner calls your function directly; you do not write `main`.

Contract: `a` and `b` are `long long` positions between -1000 and 1000 and the function returns the nonnegative distance between them as a `long long`.

## Common misconception
Keep the function name, parameter order and types unchanged because another program calls them. A by-value parameter is a copy, so changing it inside the function does not change the caller's variable; only a reference parameter (`long long&`) can do that, and this contract does not use one. Negative positions still have a nonnegative distance, and the function must work for every valid call, not only the example.

## Worked example
```cpp
long long twice(long long value) {
    return value * 2;
}

void bump(long long x) {
    x += 1;
}

long long n = 4;
long long result = twice(n);
bump(n);
```

result is 8 and n is still 4: `bump` incremented its own copy. A second call of `twice` gets a fresh parameter.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```cpp
long long distance_between(long long a, long long b) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Subtract the smaller position from the larger one, or negate a negative difference.

## Solutions
### C++
```cpp
long long distance_between(long long a, long long b) {
    return a > b ? a - b : b - a;
}
```
