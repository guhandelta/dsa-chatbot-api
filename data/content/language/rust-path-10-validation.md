---
track: language
language: rust
level: intermediate
order: 10
prerequisites: rust-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: safe_at
starter_code: "fn safe_at(values: Vec<i64>, index: i64, fallback: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# Rust: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define the behaviour for invalid input. Rust offers several failure contracts: `Option` for absence, `Result<T, E>` for an error value the caller must handle, and `panic!` for bugs. Indexing with `v[i]` panics when `i` is out of range, but `v.get(i)` returns `Option<&i64>`, which `.copied()` turns into `Option<i64>` and `.unwrap_or(x)` resolves to a plain value. Indices are `usize`, so an `i64` index must be converted; `usize::try_from(i)` (available without an import in the 2021 edition) returns an `Err` for negative numbers, whereas `as usize` silently wraps. This task chooses a fallback value, so every input in the contract is meaningful.

Contract: `values` has length 0 to 100; `index` and `fallback` are `i64` integers from -1000 to 1000. Return the element at `index` when that is a valid position, otherwise `fallback`. Never panic.

## Common misconception
`values[index as usize]` is wrong for a negative index: `-1i64 as usize` wraps to 18446744073709551615 and the indexing then panics. `as` never reports a failed conversion, so prefer a checked conversion such as `usize::try_from`. Validate negative indices as well as indices equal to or larger than the length, and do not call `unwrap()` on a `None`, which also panics.

## Worked example
```rust
fn parse_positive(text: &str) -> Result<i64, String> {
    match text.parse::<i64>() {
        Ok(n) if n > 0 => Ok(n),
        Ok(_) => Err("expected a positive value".to_string()),
        Err(_) => Err("not a number".to_string()),
    }
}

fn main() {
    println!("{:?} {:?} {:?}", parse_positive("42"), parse_positive("0"), parse_positive("4x"));
}
```

This prints `Ok(42) Err("expected a positive value") Err("not a number")`. The function reports failure through its return type instead of crashing, and the caller must handle both cases. That is one failure contract. The exercise below deliberately chooses a fallback instead, so do not copy the `Result` shape into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values is a `Vec<i64>` of length 0 to 100; all numeric inputs are `i64` integers between -1000 and 1000. Do not panic for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```rust
fn safe_at(values: Vec<i64>, index: i64, fallback: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Convert the signed index to `usize` with a checked conversion so negatives are rejected, look the position up with `get`, and use the fallback when either step fails.

## Solutions
### Rust
```rust
fn safe_at(values: Vec<i64>, index: i64, fallback: i64) -> i64 {
    match usize::try_from(index) {
        Ok(i) => values.get(i).copied().unwrap_or(fallback),
        Err(_) => fallback,
    }
}
```
