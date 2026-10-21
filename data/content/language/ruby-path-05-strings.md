---
track: language
language: ruby
level: beginner
order: 5
prerequisites: ruby-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: count_vowels
starter_code: "def count_vowels(text)\n  # Write your solution here.\nend"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# Ruby: Strings and iteration — Easy — Shared curriculum

## Learn
A `String` is an ordered sequence of characters, UTF-8 by default. Indexes start at 0 and the last valid index is `length - 1`; negative indexes count from the end. Indexing produces a one-character `String`, not a number, so compare it with strings such as `"a"`. `length` counts characters while `bytesize` counts bytes. Ruby strings are mutable (`<<` and the bang methods change the receiver), but reading characters does not modify the string. `each_char` visits one character at a time.

Contract: `count_vowels(text)` receives a string of 0 to 1000 lowercase English letters and returns how many of `a`, `e`, `i`, `o`, `u` it contains, as an `Integer`. The empty string gives 0.

## Common misconception
Indexing outside the string does not fail loudly: `"cat"[3]` is `nil` and `"cat"[-1]` is `"t"`, so an off-by-one reads `nil` or wraps around instead of raising. Passing `nil` onward then fails later; for example `"aeiou".include?(nil)` raises `TypeError`. Keep the traversal within `0` to `length - 1`, or iterate characters directly so no index is needed.

## Worked example
```ruby
word = "cat"
first = word[0]
last = word[-1]
beyond = word[3]
size = word.length
```

`first` is `"c"`, `last` is `"t"`, `beyond` is `nil` and `size` is 3. The valid indexes are 0, 1 and 2. `first.class` is `String`: Ruby has no separate character type.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```ruby
def count_vowels(text)
  # Write your solution here.
end
```

## Approach
Visit each character once, test whether it is one of the five vowels by asking a string that holds the vowels, and keep a running count that is the last expression of the method.

## Solutions
### Ruby
```ruby
def count_vowels(text)
  count = 0
  text.each_char do |ch|
    count += 1 if "aeiou".include?(ch)
  end
  count
end
```
