---
track: language
language: cpp
level: beginner
order: 2
prerequisites: cpp-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: in_range
starter_code: "bool in_range(long long value, long long low, long long high) {\n    // Write your solution here.\n    return false;\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# C++: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition has type `bool`. Combine conditions with `&&` when both must hold or `||` when either suffices; both evaluate left to right and skip the right operand once the result is already decided. Boundary words such as inclusive decide whether a comparison uses `<` or `<=`.

Contract: `value`, `low` and `high` are `long long` values from -1000 to 1000 with `low <= high`; the function returns a `bool`.

## Common misconception
A chained mathematical comparison does not mean what it says in C++. `low <= value <= high` is parsed as `(low <= value) <= high`: the first comparison yields `false` or `true` (0 or 1), and that number is then compared with `high`. It compiles, and compilers only warn about it (for example `-Wparentheses`). Write both comparisons and join them with `&&`. Likewise `if (x = 0)` assigns instead of comparing; use `==`.

## Worked example
```cpp
int age = 18;
bool can_join = age >= 16 && age <= 25;
```

Both comparisons are true, so can_join is true. Test each boundary (16 and 25) independently when translating a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```cpp
bool in_range(long long value, long long low, long long high) {
    // Write your solution here.
    return false;
}
```

## Approach
Use the language construct in this lesson. Compare against each boundary separately and join the two tests with `&&`.

## Solutions
### C++
```cpp
bool in_range(long long value, long long low, long long high) {
    return value >= low && value <= high;
}
```
