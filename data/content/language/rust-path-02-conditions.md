---
track: language
language: rust
level: beginner
order: 2
prerequisites: rust-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: in_range
starter_code: "fn in_range(value: i64, low: i64, high: i64) -> bool {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# Rust: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A comparison such as `<=` produces a `bool`. Rust has no truthiness: the condition of an `if` or `while` must be exactly a `bool`, so an integer such as `1` or `0` is a type error rather than true or false. Combine conditions with `&&` (both must hold) or `||` (either suffices); both short-circuit from left to right. `if` is itself an expression and can produce a value. Boundary words such as inclusive decide whether a comparison uses `<` or `<=`.

Contract: `value`, `low` and `high` are `i64` values from -1000 to 1000 with `low <= high`; return `true` when `value` lies between `low` and `high` with both ends counted, otherwise `false`.

## Common misconception
A chained mathematical comparison such as `low <= value <= high` is not accepted: the parser reports that comparison operators cannot be chained. Write each comparison separately and join them with `&&`. Also do not expect integers to be truthy: `if n { ... }` with an integer `n` fails to compile with a mismatched-types error.

## Worked example
```rust
fn is_weekend(day: i64) -> bool {
    day == 6 || day == 7
}

fn main() {
    let label = if is_weekend(6) { "rest" } else { "work" };
    println!("{} {} {}", is_weekend(6), is_weekend(3), label);
}
```

This prints `true false rest`. `||` is true when either side is true, and the `if` expression chooses between two values of the same type. Test each side of a written rule independently when you translate it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are `i64` integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```rust
fn in_range(value: i64, low: i64, high: i64) -> bool {
    // Write your solution here.
    todo!()
}
```

## Approach
Compare `value` with each boundary separately, using the inclusive operators, and join the two comparisons with `&&`.

## Solutions
### Rust
```rust
fn in_range(value: i64, low: i64, high: i64) -> bool {
    value >= low && value <= high
}
```
