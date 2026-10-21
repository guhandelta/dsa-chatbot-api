---
track: language
language: cpp
level: expert
order: 11
prerequisites: cpp-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: digit_sum
starter_code: "long long digit_sum(long long n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# C++: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case supplies an answer without another call, a decreasing measure explains termination, and every call has its own parameters and local variables on the call stack. Integer `/` truncates toward zero and `%` takes the sign of the dividend, so for a nonnegative `n`, `n % 10` is the last digit and `n / 10` is the number without it. Exhausting the stack is undefined behaviour and usually crashes the process; it is not an exception you can catch.

Contract: `n` is a `long long` between 0 and 1000000; return the sum of its decimal digits using recursion. For n = 0 return 0.

## Common misconception
Check that the recursive input strictly approaches the base case; a call that passes `n` unchanged never terminates and ends in a stack overflow crash, not a clean error. The result of the recursive call must contribute to the returned value. Here no flooring is needed, because integer division already truncates. This small input bound keeps the call depth tiny; deeply recursive problems may need an explicit stack, and passing a container by value in each call copies it every time.

## Worked example
```cpp
long long triangular(long long n) {
    if (n <= 0) return 0;
    return n + triangular(n - 1);
}
```

For n = 3 the calls are triangular(3), triangular(2), triangular(1), triangular(0). The base case returns 0, and 1, 2 and 3 are added as the calls return, giving 6. The measure `n` decreases by one on every call.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```cpp
long long digit_sum(long long n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. A single-digit number is its own answer; otherwise add the last digit to the answer for the rest of the number.

## Solutions
### C++
```cpp
long long digit_sum(long long n) {
    if (n < 10) {
        return n;
    }
    return n % 10 + digit_sum(n / 10);
}
```
