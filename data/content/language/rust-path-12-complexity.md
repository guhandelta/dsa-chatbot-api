---
track: language
language: rust
level: expert
order: 12
prerequisites: rust-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: has_pair
starter_code: "fn has_pair(values: Vec<i64>, target: i64) -> bool {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# Rust: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. A `HashSet` offers average constant-time `insert` and `contains` (the default hasher is SipHash, which resists hash-flooding but is slower than simple hashes), so one pass over the vector with a set gives expected linear time and linear extra space, whereas checking every pair costs quadratic time. In Rust, `contains` takes a reference (`&x`) while `insert` takes ownership; `for v in values` consumes the vector and moves each element, which is free for `i64`. An invariant states what is true before each iteration, for example: the set holds exactly the values at indices already visited.

Contract: `values` has length 0 to 1000 and elements and `target` are `i64` integers between -1000 and 1000; return whether two elements at different indices sum to `target`. Use a set to practise one-pass reasoning.

## Common misconception
Two different indices may hold the same value, so `[1, 1]` with target 2 is true, but a single `1` is not its own partner: `[1]` with target 2 is false. If you insert the current element into the set before looking for its partner, the element pairs with itself. A correct result on six tests is evidence, not proof; explain your invariant and complexity as part of your mastery check. Also try inputs whose elements are negative, since the partner `target - x` may be negative or positive and must still be found.

## Worked example
```rust
fn main() {
    let values = [4, 7, 9];
    let mut single = 0;
    let mut nested = 0;
    for _a in values.iter() {
        single += 1;
    }
    for _a in values.iter() {
        for _b in values.iter() {
            nested += 1;
        }
    }
    println!("{} {}", single, nested);
}
```

This prints `3 9`. One traversal makes n visits for n elements; nesting a complete second traversal inside each visit makes n times n. Always count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values is a `Vec<i64>` of length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```rust
fn has_pair(values: Vec<i64>, target: i64) -> bool {
    // Write your solution here.
    todo!()
}
```

## Approach
Scan once, keeping a set of the values seen so far. For each element, first check whether its complement (target minus the element) is already in the set, and only then add the element.

## Solutions
### Rust
```rust
use std::collections::HashSet;

fn has_pair(values: Vec<i64>, target: i64) -> bool {
    let mut seen: HashSet<i64> = HashSet::new();
    for v in values {
        if seen.contains(&(target - v)) {
            return true;
        }
        seen.insert(v);
    }
    false
}
```
