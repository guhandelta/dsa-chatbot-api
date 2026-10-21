---
track: language
language: rust
level: beginner
order: 4
prerequisites: rust-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: distance
starter_code: "fn distance(a: i64, b: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# Rust: Functions and contracts — Easy — Shared curriculum

## Learn
A function signature is its contract: the name, the type of every parameter, and the return type. Parameters are local bindings and are immutable unless declared `mut`. `i64` is a `Copy` type, so each call receives its own copy and the caller's variables are never changed. A function ends at a `return` or at its final expression without a semicolon, and every path must produce the declared type. Signed integers have an `abs()` method.

Contract: keep the supplied name, parameter order and `i64` types because the test runner calls the function directly. `a` and `b` are positions from -1000 to 1000; return the nonnegative distance between them.

## Common misconception
Do not switch to unsigned types because a distance is nonnegative. With `u64` or `usize`, `a - b` is computed before any absolute value could help: when `b > a` the subtraction panics with "attempt to subtract with overflow" in a debug build and silently wraps around in a release build. Negative positions also still have a nonnegative distance, and the function must work for every valid call, not only the example.

## Worked example
```rust
fn clamp_to_ten(x: i64) -> i64 {
    if x > 10 {
        return 10;
    }
    x
}

fn main() {
    println!("{} {}", clamp_to_ten(25), clamp_to_ten(4));
}
```

This prints `10 4`. The first call takes the early `return`; the second skips the `if` and falls through to the final expression `x`. Each call gets its own parameter `x`. The exercise runner calls your function directly, so no `main` is needed in your answer.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between `i64` integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an `i64`.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```rust
fn distance(a: i64, b: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Subtract one position from the other while both are still signed, then take the absolute value of the difference.

## Solutions
### Rust
```rust
fn distance(a: i64, b: i64) -> i64 {
    (a - b).abs()
}
```
