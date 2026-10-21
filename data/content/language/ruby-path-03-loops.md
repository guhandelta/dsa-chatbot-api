---
track: language
language: ruby
level: beginner
order: 3
prerequisites: ruby-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: sum_through
starter_code: "def sum_through(n)\n  # Write your solution here.\nend"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# Ruby: Loops and accumulation — Easy — Shared curriculum

## Learn
A loop repeats a body; an accumulator holds the result for everything visited so far. State what the accumulator means before and after each iteration. Ruby loops are normally iterator methods that take a block: `(1..n).each { |i| ... }`, `n.times { ... }` or `1.upto(n) { ... }`. A range `a..b` includes `b`, `a...b` excludes it, and `n.times` visits 0 through `n - 1`. A range whose start is past its end, such as `1..0`, is empty, so its block never runs. Blocks are closures: they can read and assign local variables declared outside them, but a variable first assigned inside a block does not exist after the block ends.

Contract: `sum_through(n)` receives an integer from 0 to 1000 and returns the sum of the integers 1 through `n` as an `Integer`, computed with a loop. For `n = 0` the result is 0.

## Common misconception
Two Ruby-specific traps. First, `(1...n)` and `n.times` both stop before the value you may need, so trace `n = 1` to see which numbers are visited. Second, a counter created inside the block is a fresh local on every iteration and cannot be read after the loop (referring to it raises `NameError`). Declare the accumulator before the loop so every iteration updates the same variable.

## Worked example
```ruby
product = 1
(1..3).each { |i| product *= i }
```

`product` changes from 1 to 1, then 2, then 6. Before each iteration it is the product of the integers already visited. The block updates `product` because it was assigned before the block began; changing the starting value to 0 would make every result 0.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```ruby
def sum_through(n)
  # Write your solution here.
end
```

## Approach
Start an accumulator at zero outside the loop, add each integer from 1 through `n` inside the block, and make the accumulator the last expression so it is returned. An empty range leaves it at 0.

## Solutions
### Ruby
```ruby
def sum_through(n)
  total = 0
  (1..n).each { |i| total += i }
  total
end
```
