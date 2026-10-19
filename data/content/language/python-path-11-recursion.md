---
track: language
language: python
level: expert
order: 11
prerequisites: python-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: digit_sum
starter_code: "def digit_sum(n):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# Python: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case answers without another call, and a decreasing measure explains termination. Each call has its own local variables. `functools.lru_cache` memoises repeated subproblems.

## Common misconception
Python limits recursion depth (about 1000 frames by default), so deep recursion raises RecursionError; use a loop or an explicit stack for long chains. The recursive result must contribute to the return value. Use `//`, not `/`, to shrink an int.

## Worked example
```python
def countdown(n):
    if n == 0:
        return 0
    return countdown(n - 1)
```

For n = 2 the calls are countdown(2), countdown(1), countdown(0). The base case returns 0, which flows back through both callers.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```python
def digit_sum(n):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)
```
