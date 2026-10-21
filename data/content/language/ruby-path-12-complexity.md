---
track: language
language: ruby
level: expert
order: 12
prerequisites: ruby-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: has_pair
starter_code: "require \"set\"\n\ndef has_pair(values, target)\n  # Write your solution here.\nend"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# Ruby: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes extra storage. One traversal with O(1) average set operations is O(n) expected time. In Ruby, watch for hidden loops: `Array#include?` and `index` scan the array in O(n), so calling them inside an `each` makes the whole method O(n^2), while `Set#include?` is O(1) on average. A `return` inside a block returns from the enclosing method, which makes an early exit from `each` easy. An invariant states what is true about the data structure before each iteration.

Contract: `has_pair(values, target)` receives 0 to 1000 integers and an integer `target` (all between -1000 and 1000) and returns `true` when two elements at different indexes sum to `target`, otherwise `false`. Use a set to practise one-pass reasoning.

## Common misconception
Two different indexes may hold equal values, so `[1, 1]` with target 2 is a pair, but a single `1` is not a pair with itself. Check whether the complement is already in the set before adding the current value, so an element is never its own partner. Six passing tests are evidence, not a proof; state the invariant and the complexity as part of your mastery check.

## Worked example
```ruby
values = [4, 7, 9]
visits = 0
values.each { |value| visits += 1 }
nested = 0
values.each { |a| values.each { |b| nested += 1 } }
```

`visits` is 3 for 3 elements, while `nested` is 9. A complete second traversal inside each visit creates n * n steps. Count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```ruby
require "set"

def has_pair(values, target)
  # Write your solution here.
end
```

## Approach
Keep a set of values already visited. For each value, ask the set whether the number that would complete the target has been seen before, return true if so, and only then record the current value. If the loop ends, no pair exists.

## Solutions
### Ruby
```ruby
require "set"

def has_pair(values, target)
  seen = Set.new
  values.each do |value|
    return true if seen.include?(target - value)
    seen.add(value)
  end
  false
end
```
