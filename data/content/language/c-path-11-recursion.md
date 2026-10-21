---
track: language
language: c
level: expert
order: 11
prerequisites: c-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: digit_sum
starter_code: "long long digit_sum(long long n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# C: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case returns an answer without another call; a decreasing measure explains why the calls terminate. Every call gets its own automatic variables on the call stack. C does not guarantee tail-call optimization, and the stack size is set by the platform, so very deep recursion, or a missing base case, exhausts the stack and typically crashes the program; there is no exception to catch. Integer `/` truncates toward zero and `%` takes the sign of the dividend; for nonnegative operands `n / 10` removes the last decimal digit and `n % 10` is that digit.

The contract here: `n` is an integer from 0 to 1000000, and the function returns the sum of its decimal digits using recursion. For `n = 0` the result is 0. The depth is at most seven calls.

## Common misconception
A recursive call's result must contribute to what you return. Writing `digit_sum(n / 10);` as a statement, and then returning only `n % 10`, compiles without complaint and silently discards the recursive answer, so `digit_sum(123)` returns 3 instead of 6. Also check that every call moves strictly toward the base case: an argument that does not shrink recurses until the stack is exhausted.

## Worked example
```c
long long power(long long base, int exponent) {
    if (exponent == 0) return 1;
    return base * power(base, exponent - 1);
}
```

For `power(2, 3)` the calls are `power(2, 3)`, `power(2, 2)`, `power(2, 1)`, `power(2, 0)`. The base case returns 1, and each caller multiplies it by 2 on the way back: 2, 4, 8. The exponent decreases by one each time, so it reaches 0. This example assumes a nonnegative exponent and a result that fits in `long long`; a negative exponent would never reach the base case.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```c
long long digit_sum(long long n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Choose the base case for a single digit (any value below 10 is its own digit sum). Otherwise split n into its last digit and the remaining number, recurse on the remaining number, and add the last digit to the returned result.

## Solutions
### C
```c
long long digit_sum(long long n) {
    if (n < 10) {
        return n;
    }
    return n % 10 + digit_sum(n / 10);
}
```
