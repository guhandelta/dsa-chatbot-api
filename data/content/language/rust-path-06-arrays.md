---
track: language
language: rust
level: intermediate
order: 6
prerequisites: rust-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: count_above
starter_code: "fn count_above(values: Vec<i64>, threshold: i64) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# Rust: Arrays and lists — Easy — Shared curriculum

## Learn
`Vec<i64>` is an owned, growable array; `[i64; N]` is a fixed-size array; `&[i64]` is a borrowed slice of either. Indices are `usize`. `v[i]` panics when `i` is out of range, while `v.get(i)` returns an `Option`. Passing a `Vec` by value moves it into the callee: the caller can no longer use it. To read without taking ownership, borrow it (`&values`, or `values.iter()`). Iterating `for x in values` consumes the vector, whereas `for x in &values` borrows it.

Contract: `values` has length 0 to 1000; its elements and `threshold` are `i64` integers from -1000 to 1000. Return how many elements are strictly greater than `threshold`, as an `i64`. Do not modify `values`: do not declare it `mut`.

## Common misconception
Assignment moves a `Vec`; it does not alias it. After `let alias = scores;` the name `scores` is gone and using it is the error "borrow of moved value" (E0382). An independent copy needs `.clone()`, and a read-only view needs a borrow. Also remember that strictly greater excludes equal values, so `[2, 2]` with threshold 2 gives 0.

## Worked example
```rust
fn main() {
    let scores = vec![3, 8];
    let mut copy = scores.clone();
    copy[0] = 5;
    println!("{:?} {:?}", scores, copy);
    let moved = scores;
    println!("{:?}", moved);
}
```

This prints `[3, 8] [5, 8]` and then `[3, 8]`. `clone()` makes a separate vector, so changing `copy` leaves `scores` intact. The plain `let moved = scores;` transfers ownership instead of copying; after that line `scores` could no longer be used.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values is a `Vec<i64>` of length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```rust
fn count_above(values: Vec<i64>, threshold: i64) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Walk over the elements by reference, keep those strictly greater than the threshold, count them, and convert the count to `i64`.

## Solutions
### Rust
```rust
fn count_above(values: Vec<i64>, threshold: i64) -> i64 {
    values.iter().filter(|&&v| v > threshold).count() as i64
}
```
