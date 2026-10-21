---
track: language
language: ruby
level: intermediate
order: 8
prerequisites: ruby-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: unique_count
starter_code: "require \"set\"\n\ndef unique_count(values)\n  # Write your solution here.\nend"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# Ruby: Sets and equality — Easy — Shared curriculum

## Learn
A `Set` holds unique elements. It is built on a `Hash`, so `add`, `delete` and `include?` are O(1) on average, and adding a duplicate does not change `size`. `Set` is loaded automatically only from Ruby 3.2; on Ruby 3.1 and older, using `Set` without `require "set"` raises `NameError`, so write the `require` and the code works on every version. `add` always returns the set (which is truthy); `add?` returns the set when it inserted and `nil` when the element was already present. Two sets are equal when they hold the same elements in any order. Elements are compared like hash keys, with `eql?` and `hash`, so `1` and `1.0` are different elements even though `1 == 1.0` is true.

Contract: `unique_count(values)` receives 0 to 1000 integers between -1000 and 1000 and returns how many distinct values it contains, as an `Integer`, using a set.

## Common misconception
`Set#add` returns the set itself, which is always truthy, so it cannot tell you whether the element was new; use `add?` for that. Do not depend on a numeric-looking `==`: set membership follows `eql?`, so `Set[1, 1.0].size` is 2. `Set.new` expects an enumerable such as an array; `Set.new(5)` raises an error. The values here are all integers, so no such mix occurs, but your reasoning about equality should name the rule. Count the values exactly as given: `-1` and `1` are distinct, so transforming them first (for example with `abs`) would merge entries wrongly, and the shared tests alone would not catch that.

## Worked example
```ruby
require "set"
visited = Set.new
visited << 7
visited << 7
found = visited.include?(7)
size = visited.size
```

`found` is `true` and `size` is 1. `<<` is an alias of `add`, and adding 7 a second time creates no second entry.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```ruby
require "set"

def unique_count(values)
  # Write your solution here.
end
```

## Approach
Put the values into a set, which discards duplicates, and return the set's size. The empty array produces an empty set of size 0.

## Solutions
### Ruby
```ruby
require "set"

def unique_count(values)
  Set.new(values).size
end
```
