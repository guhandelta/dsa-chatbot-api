---
track: language
language: rust
level: beginner
order: 3
prerequisites: rust-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: sum_through
starter_code: "fn sum_through(n: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# Rust: Loops and accumulation — Easy — Shared curriculum

## Learn
A `for` loop walks a range: `a..b` stops before `b`, while `a..=b` includes it. A range whose start is past its end is empty, so the body runs zero times. Variables are immutable by default, so an accumulator that changes on every iteration must be declared with `let mut`. The loop variable takes its type from the surrounding code, here `i64`. State what the accumulator means before and after each iteration; that statement is the loop invariant.

Contract: `n` is an `i64` from 0 to 1000; return the sum of every integer from 1 through `n`, computed with a loop. For `n = 0` return 0.

## Common misconception
`1..n` excludes `n`, which is the classic off-by-one; `1..=n` includes it. Check `n = 0` and `n = 1` by tracing the range, the update, and the return. A second trap is forgetting `mut`: `let total = 0;` followed by `total += i;` does not compile (cannot assign twice to immutable variable).

## Worked example
```rust
fn main() {
    let mut product: i64 = 1;
    for i in 1..=3 {
        product *= i;
    }
    println!("{} {}", product, (1..3).count());
}
```

This prints `6 2`. `product` goes 1, 1, 2, 6; before each iteration it holds the product of the integers already visited. The half-open range `1..3` visits only two values, which is why `1..=3` is used for the loop. Starting the product at 0 would make every result 0.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an `i64` integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```rust
fn sum_through(n: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Declare a mutable accumulator outside the loop, add each value of the inclusive range `1..=n` to it, and return it after the loop.

## Solutions
### Rust
```rust
fn sum_through(n: i64) -> i64 {
    let mut total = 0;
    for i in 1..=n {
        total += i;
    }
    total
}
```
