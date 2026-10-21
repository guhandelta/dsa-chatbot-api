---
track: language
language: c
level: beginner
order: 2
prerequisites: c-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: in_range
starter_code: "#include <stdbool.h>\n\nbool in_range(long long value, long long low, long long high) {\n    // Write your solution here.\n    return false;\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# C: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition in C is an expression whose value is zero (false) or nonzero (true). Comparison and logical operators produce the `int` values 1 or 0; `<stdbool.h>` adds the names `bool`, `true` and `false` for readability. `&&` requires both sides and `||` requires either; both evaluate left to right and stop as soon as the answer is known. Words such as "inclusive" decide between `<` and `<=`.

The contract here: `low <= high`, all three arguments are integers from -1000 to 1000, and the function returns `true` exactly when `value` lies between `low` and `high`, including both boundaries. When `low == high` only that single value qualifies.

## Common misconception
A mathematical chain such as `low <= value <= high` is valid C but does not mean what it means on paper: it parses as `(low <= value) <= high`. The first comparison produces 0 or 1, and that number is then compared with `high`. With `low = 1`, `value = 0`, `high = 5` the chain evaluates to 1 (true) although 0 is outside 1..5. The compiler warns with `-Wparentheses` under `-Wall`. Write each comparison out and join them with `&&`.

## Worked example
```c
int age = 18;
bool can_join = age >= 16 && age <= 25;
```

Both comparisons are 1, so `can_join` is true (printing it with `%d` shows 1). Test each boundary independently when translating a written rule: 15 and 26 are false, 16 and 25 are true.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```c
#include <stdbool.h>

bool in_range(long long value, long long low, long long high) {
    // Write your solution here.
    return false;
}
```

## Approach
Express "at least low" and "at most high" as two separate comparisons and join them with `&&`. Do not chain the comparisons; test the cases where `value` equals `low` and where it equals `high`.

## Solutions
### C
```c
#include <stdbool.h>

bool in_range(long long value, long long low, long long high) {
    return value >= low && value <= high;
}
```
