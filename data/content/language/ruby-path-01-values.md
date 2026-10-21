---
track: language
language: ruby
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: total_cost
starter_code: "def total_cost(price, quantity)\n  # Write your solution here.\nend"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# Ruby: Values and arithmetic — Easy — Shared curriculum

## Learn
Every Ruby value is an object, including integers, so `price * quantity` is a method call on an `Integer` that returns a new `Integer`. `Integer` has arbitrary precision, so a product never overflows a fixed width; the largest result in this exercise is 1000000. Integer `/` floors toward negative infinity, `%` takes the sign of the divisor, and `fdiv` returns a `Float`. A Ruby method returns the value of the last expression it evaluates, so the result has to be what the method evaluates last, not something it prints.

Contract: `total_cost(price, quantity)` receives two `Integer` values from 0 to 1000 and returns an `Integer`. If either input is 0 the cost is 0.

## Common misconception
`puts` writes text and returns `nil`. If the last line of your method is `puts price * quantity`, the caller receives `nil` and the tests see no result. Also remember that `*` depends on the receiver's class: `3 * 4` is `12`, but `"3" * 4` repeats the string and gives `"3333"`. Work with the Integers you were given and do not convert them to strings.

## Worked example
```ruby
hours = 2
minutes = hours * 60
chunks = minutes / 7
leftover = minutes % 7
```

`minutes` is 120, `chunks` is 17 and `leftover` is 1, because 17 * 7 + 1 == 120. Integer division discards the fraction and floors, so `-7 / 2` is -4, not -3. Assigning each step to a descriptive name makes the arithmetic readable.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```ruby
def total_cost(price, quantity)
  # Write your solution here.
end
```

## Approach
Multiply the two Integers and let the multiplication be the last expression of the method, so it becomes the return value without an explicit `return` or any printing.

## Solutions
### Ruby
```ruby
def total_cost(price, quantity)
  price * quantity
end
```
