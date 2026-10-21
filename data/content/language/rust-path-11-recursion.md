---
track: language
language: rust
level: expert
order: 11
prerequisites: rust-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: digit_sum
starter_code: "fn digit_sum(n: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# Rust: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case supplies an answer without another call. A decreasing measure explains termination, and each call has its own local variables and its own stack frame. In Rust a function may call itself directly; do not count on tail-call optimisation, and the size of the main-thread stack is determined outside Rust, so deeply recursive problems need an explicit stack or a loop. Integer `/` truncates toward zero and `%` takes the sign of the dividend, so for a nonnegative `n`, `n % 10` is the last decimal digit and `n / 10` removes it.

Contract: `n` is an `i64` from 0 to 1000000; return the sum of its decimal digits using recursion. For `n = 0` return 0.

## Common misconception
Check that the recursive input strictly approaches the base case: `n / 10` shrinks `n` until it reaches 0. The result of the recursive call must contribute to the returned value; a recursive call ended with a semicolon is evaluated and thrown away, and then the block's value is `()`, which the compiler rejects as a mismatched type. The small input bound keeps the call depth at no more than eight here, but recursion depth is a real limit in Rust. Trace a number with more than three digits (such as 1000000) by hand as well as the single-digit cases, because the base case and the shrinking step must hold for every digit count.

## Worked example
```rust
fn pow2(n: i64) -> i64 {
    if n == 0 {
        1
    } else {
        2 * pow2(n - 1)
    }
}

fn main() {
    println!("{}", pow2(3));
}
```

This prints `8`. For `n = 3` the calls are `pow2(3)`, `pow2(2)`, `pow2(1)`, `pow2(0)`. The base case returns 1, and each caller multiplies by 2 on the way back: 2, 4, 8. The measure `n` drops by one per call, which guarantees termination for nonnegative inputs.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an `i64` integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```rust
fn digit_sum(n: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Return 0 for the base case. Otherwise combine the last digit with the digit sum of the number that remains after dropping that digit.

## Solutions
### Rust
```rust
fn digit_sum(n: i64) -> i64 {
    if n == 0 {
        0
    } else {
        n % 10 + digit_sum(n / 10)
    }
}
```
