---
track: language
language: ruby
level: beginner
order: 4
prerequisites: ruby-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: distance
starter_code: "def distance(a, b)\n  # Write your solution here.\nend"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# Ruby: Functions and contracts — Easy — Shared curriculum

## Learn
A method contract names its parameters, return value and valid inputs. Parameters are local names for the arguments of one call, and Ruby methods check the argument count strictly: calling a two-parameter method with one argument raises `ArgumentError`. A method returns the value of its last evaluated expression; `return` is only needed for an early exit. Printing does not satisfy a return-value contract. Small methods with one purpose are easiest to verify.

Contract: `distance(a, b)` receives two integers between -1000 and 1000 and returns their nonnegative distance as an `Integer`. Keep the supplied name and argument order, because another program calls the method.

## Common misconception
Subtraction can be negative, and the distance is not: `2 - 5` is -3 but the distance between 2 and 5 is 3, whichever argument comes first. Remember also that a method whose last line is `puts` returns `nil`, and a method ending in an `if` with no `else` returns `nil` when the condition is false. A method must produce the right value on every valid call, not only the example.

## Worked example
```ruby
def double(value)
  value * 2
end
result = double(4)
```

The argument 4 becomes the parameter `value` for this call, and the last expression `value * 2` is returned, so `result` is 8. A second call gets its own `value`. The exercise runner calls your top-level method by name; you do not need a main program.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied method signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```ruby
def distance(a, b)
  # Write your solution here.
end
```

## Approach
The distance is the size of the difference, ignoring its sign. Compute the difference once and use an `Integer` method that drops the sign as the last expression.

## Solutions
### Ruby
```ruby
def distance(a, b)
  (a - b).abs
end
```
