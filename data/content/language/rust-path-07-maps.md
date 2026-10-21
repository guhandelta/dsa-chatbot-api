---
track: language
language: rust
level: intermediate
order: 7
prerequisites: rust-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: count_target
starter_code: "fn count_target(words: Vec<String>, target: String) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# Rust: Maps and frequency counting — Easy — Shared curriculum

## Learn
`HashMap<K, V>` from `std::collections` associates keys with values. `insert(k, v)` stores a pair, `get(&k)` returns an `Option<&V>` (`None` for a missing key), and `entry(k).or_insert(default)` returns a mutable reference to the value, creating it first when the key is absent, which makes counting a one-liner: dereference and add. Keys are compared by value, so two different `String`s with the same text are the same key. Iteration order of a `HashMap` is unspecified and can differ between runs; use `BTreeMap` when deterministic order matters.

Contract: `words` has 0 to 100 lowercase words of length 1 to 20 and `target` follows the same rule. Return how many times `target` occurs in `words`, as an `i64`; a word that never appeared counts 0. Building a frequency map is the practice technique.

## Common misconception
Indexing a map with a missing key, as in `counts[&key]`, panics ("no entry found for key"); `get` returns an `Option` so the missing case is handled explicitly. Do not assume every queried word has appeared. Words are compared as whole strings: "a" does not match "aa".

## Worked example
```rust
use std::collections::HashMap;

fn main() {
    let mut ages: HashMap<String, i64> = HashMap::new();
    ages.insert("Ada".to_string(), 30);
    println!("{:?} {:?} {}", ages.get("Ada"), ages.get("Bob"), ages.contains_key("Ada"));
}
```

This prints `Some(30) None true`. "Ada" is the key and 30 is the value; the lookup of the absent key "Bob" returns `None` rather than a default or a crash. Here `insert` takes ownership of the key `String`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words is a `Vec<String>` of 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule. Return the count as an `i64`.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```rust
fn count_target(words: Vec<String>, target: String) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Walk the words, bump the count stored under each word in a `HashMap<String, i64>` using the entry API, then look up `target` and fall back to 0 when it never appeared.

## Solutions
### Rust
```rust
use std::collections::HashMap;

fn count_target(words: Vec<String>, target: String) -> i64 {
    let mut counts: HashMap<String, i64> = HashMap::new();
    for word in words {
        *counts.entry(word).or_insert(0) += 1;
    }
    counts.get(&target).copied().unwrap_or(0)
}
```
