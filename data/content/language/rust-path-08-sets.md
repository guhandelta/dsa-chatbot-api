---
track: language
language: rust
level: intermediate
order: 8
prerequisites: rust-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: unique_count
starter_code: "fn unique_count(values: Vec<i64>) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# Rust: Sets and equality — Easy — Shared curriculum

## Learn
`HashSet<T>` from `std::collections` records membership and stores each distinct element once. `insert(x)` returns a `bool`: `true` when `x` was new and `false` when it was already present, in which case the size does not change. `contains(&x)` tests membership and `len()` gives the number of distinct elements. Element types must implement `Eq` and `Hash`; `i64` and `String` do, but `f64` does not (it is only `PartialEq`/`PartialOrd`). A set can be built directly from an iterator with `collect()`. Choose a set when you need uniqueness and a map when each key also carries a value.

Contract: `values` has 0 to 1000 `i64` integers between -1000 and 1000; return the number of distinct values, as an `i64`.

## Common misconception
Do not depend on the iteration order of a hash set: it is unspecified and may differ between runs, so never turn it into output without sorting. Remember that a set cannot hold floats directly: `HashSet<f64>` does not compile because `f64` is not `Eq + Hash` (the `insert` method's trait bounds are not satisfied). Adding the same integer twice never creates two entries, but equality is exact: -3 and 3 are different elements, so store each value as given instead of normalising it first. Also check inputs that contain duplicates and negatives, not just a short list of non-negative values.

## Worked example
```rust
use std::collections::HashSet;

fn main() {
    let mut visited: HashSet<i64> = HashSet::new();
    let first = visited.insert(7);
    let second = visited.insert(7);
    println!("{} {} {} {}", first, second, visited.len(), visited.contains(&7));
}
```

This prints `true false 1 true`. The second `insert` finds 7 already present, returns `false`, and leaves the set with one element. `contains` takes a reference to the value being looked up.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values is a `Vec<i64>` of 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```rust
fn unique_count(values: Vec<i64>) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Put every element into a `HashSet<i64>` (for example by collecting the vector into one) and return the set's length as an `i64`.

## Solutions
### Rust
```rust
use std::collections::HashSet;

fn unique_count(values: Vec<i64>) -> i64 {
    let distinct: HashSet<i64> = values.into_iter().collect();
    distinct.len() as i64
}
```
