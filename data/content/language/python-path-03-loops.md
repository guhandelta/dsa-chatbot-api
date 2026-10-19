---
track: language
language: python
level: beginner
order: 3
prerequisites: python-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: sum_through
starter_code: "def sum_through(n):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# Python: Loops and accumulation — Easy — Shared curriculum

## Learn
A loop repeats a body for each value it visits. `range(1, n + 1)` visits 1 through n because the stop value is excluded. An accumulator stores the result of everything visited so far; say what it means before and after each iteration.

## Common misconception
An off-by-one error changes which values are visited: `range(n)` stops at n - 1. Check n = 0 and n = 1 by tracing start, stop and the accumulator. Initialise the accumulator before the loop so it survives each iteration.

## Worked example
```python
product = 1
for i in range(1, 4):
    product *= i
```

product goes 1, 2, 6. Before each iteration it is the product of the integers visited so far; starting it at 0 would make every result 0.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```python
def sum_through(n):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def sum_through(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total
```
