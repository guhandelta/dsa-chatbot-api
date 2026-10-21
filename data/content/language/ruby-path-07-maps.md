---
track: language
language: ruby
level: intermediate
order: 7
prerequisites: ruby-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: count_target
starter_code: "def count_target(words, target)\n  # Write your solution here.\nend"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# Ruby: Maps and frequency counting — Easy — Shared curriculum

## Learn
A `Hash` stores key-value pairs with O(1) average lookup, insert and delete, and iterates in insertion order. A frequency map keeps how many times each key has appeared. Reading a missing key returns `nil` unless the hash has a default: `Hash.new(0)` gives every missing key the default 0, while `fetch(key)` raises `KeyError` and `fetch(key, default)` returns an explicit fallback. Keys are compared with `eql?` and `hash`, so equal strings are the same key, and the symbol `:a` and the string `"a"` are different keys.

Contract: `count_target(words, target)` receives 0 to 100 lowercase English words, each 1 to 20 letters long, plus a target word of the same form, and returns how many times `target` occurs as a whole word. Build a frequency map as the practice technique.

## Common misconception
On a plain `{}`, `counts[word] += 1` expands to `counts[word] = counts[word] + 1`; the first read is `nil` and `nil + 1` raises `NoMethodError`. `Hash.new([])` is not the fix for counters: it returns one shared default array that is never stored. Use an integer default (integers are immutable, so `Hash.new(0)` is safe). Also compare whole words: `"a"` is not an occurrence of `"aa"`.

## Worked example
```ruby
ages = { "Ada" => 30 }
known = ages.key?("Ada")
missing = ages["Bob"]
fallback = ages.fetch("Bob", 0)
```

`known` is `true`, `missing` is `nil` and `fallback` is 0. `"Ada"` is the key and 30 the value. `ages` was not changed by the lookups of `"Bob"`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```ruby
def count_target(words, target)
  # Write your solution here.
end
```

## Approach
Create a hash whose missing keys read as zero, add one for each word as you traverse, and then read the entry for the target. Reading a missing target must give 0.

## Solutions
### Ruby
```ruby
def count_target(words, target)
  counts = Hash.new(0)
  words.each { |word| counts[word] += 1 }
  counts[target]
end
```
