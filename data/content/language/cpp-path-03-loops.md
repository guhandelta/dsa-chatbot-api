---
track: language
language: cpp
level: beginner
order: 3
prerequisites: cpp-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: sum_through
starter_code: "long long sum_through(long long n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# C++: Loops and accumulation — Easy — Shared curriculum

## Learn
A `for` loop has an initializer, a condition checked before every iteration, and an update. An accumulator stores the result for everything visited so far; say what it means before and after each iteration, and give it a type wide enough for the total (`long long` here).

Contract: `n` is a `long long` between 0 and 1000 and the function returns the sum of the integers from 1 through n. When n is 0 the body never runs and the answer is 0.

## Common misconception
An off-by-one error changes which values are visited: check n = 0 and n = 1 by tracing the initializer, condition, update and return. Declare the accumulator outside the loop so it survives each iteration. Be careful with unsigned loop variables: an unsigned value is never negative, it wraps, so `for (std::size_t i = n; i >= 0; --i)` can never finish; `i >= 0` is always true and `0 - 1` wraps to the largest `std::size_t`.

## Worked example
```cpp
long long product = 1;
for (int i = 1; i <= 4; ++i) {
    product *= i;
}
```

product changes from 1 to 1, 2, 6 and finally 24. Before each iteration it is the product of the integers already visited. Starting from 0 instead of 1 would make every result 0.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```cpp
long long sum_through(long long n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Keep a `long long` accumulator outside the loop and add each integer from 1 through n.

## Solutions
### C++
```cpp
long long sum_through(long long n) {
    long long total = 0;
    for (long long i = 1; i <= n; ++i) {
        total += i;
    }
    return total;
}
```
