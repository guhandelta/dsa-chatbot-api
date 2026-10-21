---
track: language
language: ruby
level: beginner
order: 2
prerequisites: ruby-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: in_range
starter_code: "def in_range(value, low, high)\n  # Write your solution here.\nend"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# Ruby: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition evaluates to a truthy or falsy value. In Ruby only `nil` and `false` are falsy: `0` and the empty string are truthy, unlike in C or JavaScript. Comparison operators such as `>=` and `<=` return exactly `true` or `false`. Join conditions with `&&` when both must hold or `||` when either suffices; the keyword forms `and` and `or` bind much more loosely and are meant for control flow. An inclusive boundary means the comparison must accept equality (`<=` or `>=`).

Contract: `in_range(value, low, high)` returns `true` or `false`. `low <= high`, all values are integers between -1000 and 1000, and `value` equal to either bound counts as inside.

## Common misconception
A mathematical chain such as `low <= value <= high` is not a range test in Ruby. It parses as `(low <= value) <= high`, which tries to compare `true` or `false` with an Integer and raises `NoMethodError`. Write both comparisons explicitly and join them. Also return a real boolean: returning `1` or `0` would be truthy either way, because `0` is truthy in Ruby.

## Worked example
```ruby
hour = 9
open_now = hour >= 9 && hour < 17
at_five = 17 >= 9 && 17 < 17
```

`open_now` is `true`: the lower bound is inclusive. At 17 the second comparison is false because the upper bound is exclusive, so `at_five` is `false`. Test each boundary independently when translating a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```ruby
def in_range(value, low, high)
  # Write your solution here.
end
```

## Approach
Write one comparison for the lower boundary and one for the upper boundary, both allowing equality, and combine them with `&&`. The combined expression is already the boolean to return.

## Solutions
### Ruby
```ruby
def in_range(value, low, high)
  value >= low && value <= high
end
```
