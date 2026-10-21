---
track: language
language: ruby
level: intermediate
order: 10
prerequisites: ruby-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: safe_at
starter_code: "def safe_at(values, index, fallback)\n  # Write your solution here.\nend"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# Ruby: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define what happens for invalid input: a fallback value, a structured error or an exception. This task chooses a fallback. In Ruby `array[i]` returns `nil` for an index past the end instead of raising, `array.fetch(i)` raises `IndexError`, and `array.fetch(i, default)` returns the default when the index is out of range. Negative indexes are valid in Ruby and count from the end, so `[2, 4][-1]` is 4.

Contract: `safe_at(values, index, fallback)` returns `values[index]` when `index` is a valid position from 0 to `length - 1`, and `fallback` otherwise. `values` has 0 to 100 elements and all numbers are integers between -1000 and 1000. Do not raise for an invalid index.

## Common misconception
In this contract a negative index is invalid, but Ruby treats it as valid: `[2, 4][-1]` is 4, and even `[2, 4].fetch(-1, 9)` returns 4, not 9. So neither `values[index] || fallback` nor `fetch(index, fallback)` meets the contract on its own. Check the lower and upper bounds explicitly. A bare `rescue` that hides errors can conceal unrelated defects, and it would not help here because no exception is raised.

## Worked example
```ruby
def positive(value)
  raise ArgumentError, "expected a positive value" unless value > 0
  value
end
```

`positive(3)` returns 3 and `positive(0)` raises `ArgumentError`. That is one failure contract: an exception. The exercise below deliberately chooses a fallback value instead, so do not copy the raising behaviour into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```ruby
def safe_at(values, index, fallback)
  # Write your solution here.
end
```

## Approach
Decide first whether the index is outside the valid positions, covering both ends, and return the fallback early in that case. Otherwise read the element with ordinary indexing.

## Solutions
### Ruby
```ruby
def safe_at(values, index, fallback)
  return fallback if index < 0 || index >= values.length
  values[index]
end
```
