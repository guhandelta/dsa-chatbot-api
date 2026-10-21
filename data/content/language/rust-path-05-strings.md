---
track: language
language: rust
level: beginner
order: 5
prerequisites: rust-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: count_vowels
starter_code: "fn count_vowels(text: String) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# Rust: Strings and iteration — Easy — Shared curriculum

## Learn
Rust has two main string types: `String` (owned, growable) and `&str` (a borrowed view); both always hold valid UTF-8. This exercise passes you an owned `String`; inside the function you can borrow it freely. Indexing like `text[i]` is not allowed. Instead, `text.chars()` iterates Unicode characters and `text.as_bytes()` gives the underlying bytes. `len()` counts bytes, not characters. A `char` literal uses single quotes (`'a'`) and a string literal uses double quotes (`"a"`). Iterator `count()` returns a `usize`, and Rust never converts to `i64` implicitly, so cast with `as`.

Contract: `text` contains only lowercase English letters and has length 0 to 1000, so bytes and characters coincide; return how many are one of a, e, i, o, u as an `i64`.

## Common misconception
`len()` is a byte count, not a character count: the one-character string "é" has length 2 but `chars().count()` is 1. There is no `text[0]`; the compiler says the type `str` cannot be indexed by an integer. Within this exercise's lowercase ASCII input the two counts agree, but any wider contract needs a definition of "character" before it needs a loop.

## Worked example
```rust
fn main() {
    let word = String::from("cat");
    let first = word.chars().next();
    let length = word.len();
    let reversed: String = word.chars().rev().collect();
    println!("{:?} {} {}", first, length, reversed);
}
```

This prints `Some('c') 3 tac`. `next()` returns an `Option<char>` because a string may be empty. The original `word` is unchanged: inspecting or iterating does not modify it, and building `reversed` created a new `String`. Valid positions are 0, 1 and 2, but you reach them through iterators or bytes, not by `word[i]`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text is a `String` containing only lowercase English letters and has length 0 to 1000. Return the count as an `i64`.

## Example
Arguments: `[""]` → `0`

## Starter code
```rust
fn count_vowels(text: String) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Iterate over the characters of the string, keep the ones that are vowels, count them, and convert the `usize` count to `i64`.

## Solutions
### Rust
```rust
fn count_vowels(text: String) -> i64 {
    text.chars()
        .filter(|&c| matches!(c, 'a' | 'e' | 'i' | 'o' | 'u'))
        .count() as i64
}
```
