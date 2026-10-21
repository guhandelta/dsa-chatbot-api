---
track: language
language: ruby
level: expert
order: 11
prerequisites: ruby-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: digit_sum
starter_code: "def digit_sum(n)\n  # Write your solution here.\nend"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# Ruby: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive method solves a smaller instance of the same contract. The base case answers without another call, a decreasing measure explains termination, and every call has its own local variables and return point. In Ruby a method's value is its last evaluated expression, so a recursive call only contributes to the result if its value is part of that expression. Integer `/` floors, so dividing an `Integer` by 10 removes its last decimal digit, and `%` 10 reads it. Recursion depth is limited by the VM stack and the limit depends on the implementation, so this exercise keeps inputs small. `SystemStackError` is not a `StandardError`, so a bare `rescue` does not catch it.

Contract: `digit_sum(n)` receives an integer from 0 to 1000000 and returns the sum of its decimal digits using recursion. `digit_sum(0)` is 0.

## Common misconception
Because the last expression is returned, computing a digit and then ending the method with only the recursive call silently drops that digit. A method like `def wrong(n); return n if n < 10; digit = n % 10; wrong(n / 10); end` returns 1 for 123, not 6, and Ruby raises no error. Make sure each call combines its own digit with the value returned by the smaller call, and that the argument strictly shrinks toward the base case.

## Worked example
```ruby
def power_of_two(n)
  return 1 if n == 0
  2 * power_of_two(n - 1)
end
```

For `n = 2` the calls are `power_of_two(2)`, `power_of_two(1)` and `power_of_two(0)`. The base case returns 1, then 2 * 1 returns 2, then 2 * 2 returns 4. The measure `n` drops by 1 each call; the example assumes `n` is nonnegative.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```ruby
def digit_sum(n)
  # Write your solution here.
end
```

## Approach
A number below 10 is its own digit sum. For larger numbers, add the last digit to the digit sum of the number with that digit removed, and make that sum the value the method returns. Integer `/` already discards the fraction.

## Solutions
### Ruby
```ruby
def digit_sum(n)
  return n if n < 10
  n % 10 + digit_sum(n / 10)
end
```
