---
track: language
language: c
level: beginner
order: 3
prerequisites: c-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: sum_through
starter_code: "long long sum_through(long long n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# C: Loops and accumulation — Easy — Shared curriculum

## Learn
A `for` loop packs initialization, condition and update into one header: `for (init; condition; update)`. The body repeats while the condition is nonzero. An accumulator holds the result for everything visited so far; say what it means before the first iteration and after each one. Give the counter the same type as the bound it is compared with, and a type wide enough for the sums you build (`long long` here).

The contract here: `n` is an integer from 0 to 1000, and the function returns the sum of the integers 1 through n inclusive. For `n = 0` there is nothing to add and the result is 0.

## Common misconception
A local variable in C is not zero-initialized: an automatic variable that is declared without an initializer holds an indeterminate value, and reading it is a bug. `long long total;` followed by `total += i` starts from garbage. Initialize the accumulator explicitly (`= 0`) and declare it outside the loop so it survives every iteration. The second classic error is the boundary: `i < n` stops one iteration early and omits n itself. Check `n = 0` and `n = 1` by tracing initialization, condition, update and return.

## Worked example
```c
long long total = 0;
for (long long i = 1; i <= 4; i++) {
    total += 2 * i - 1;
}
```

`total` takes the values 0, 1, 4, 9, 16: after each iteration it is the sum of the odd numbers visited so far, and the final value is 16. Starting `total` at 1 would shift every result by one, and writing `i < 4` would stop at 9.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```c
long long sum_through(long long n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Start an accumulator at 0, loop the counter from 1 while it is less than or equal to `n`, and add the counter each time. The loop body never runs for `n = 0`, so the initial value is the answer there.

## Solutions
### C
```c
long long sum_through(long long n) {
    long long total = 0;
    for (long long i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}
```
