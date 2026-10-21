---
track: language
language: rust
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: total_cost
starter_code: "fn total_cost(price: i64, quantity: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# Rust: Values and arithmetic — Easy — Shared curriculum

## Learn
Every value in Rust has a type fixed at compile time. This exercise uses `i64`, a signed 64-bit integer, for both inputs and the result. Rust never converts between numeric types implicitly: an `i32` and an `i64` cannot be multiplied until one is cast with `as`. Integer overflow panics when overflow checks are enabled (the Cargo dev profile) and wraps when they are disabled (the release profile); `checked_mul`, `wrapping_mul` and `saturating_mul` let you choose the behaviour explicitly. The body of a function is a block, and a block is an expression: its last expression, written without a trailing semicolon, is the value returned to the caller. Printing is not returning.

Contract: both inputs are `i64` values from 0 to 1000, the result is their product as an `i64`, and a zero in either argument gives 0.

## Common misconception
A trailing semicolon turns the final expression into a statement, so the block's value becomes `()` instead of `i64` and the compiler rejects the function with a mismatched-types error (expected `i64`, found `()`). The other trap is assuming integers have no width: Rust has no arbitrary-precision default, so a much narrower type such as `i16` (maximum 32767) overflows on a product like 1000 × 1000 where `i64` does not; choose a width from the largest value you must hold, and keep the supplied `i64` signature.

## Worked example
```rust
fn minutes_in(hours: i64) -> i64 {
    hours * 60
}

fn main() {
    let minutes = minutes_in(2);
    println!("{}", minutes);
}
```

This prints 120. `hours * 60` has no semicolon, so it is the block's value and therefore the return value; the literal 60 is inferred to be an `i64` from the signature. Binding the result to the descriptive name `minutes` stores it for later use.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are `i64` integers from 0 to 1000, so the result fits comfortably in an `i64`.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```rust
fn total_cost(price: i64, quantity: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Multiply the two parameters and let that product be the function's last expression, without a trailing semicolon.

## Solutions
### Rust
```rust
fn total_cost(price: i64, quantity: i64) -> i64 {
    price * quantity
}
```
