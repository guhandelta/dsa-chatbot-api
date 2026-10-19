---
track: language
language: python
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: total_cost
starter_code: "def total_cost(price, quantity):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# Python: Values and arithmetic — Easy — Shared curriculum

## Learn
Expressions combine values into a new value. Python ints are unbounded, so `1000 * 1000` never overflows the way a fixed-width int can. `/` always produces a float while `//` floors to an int, and every value has a truthiness: `0`, `''`, `[]` and `None` are falsy. A function returns its result to the caller rather than printing it.

## Common misconception
`/` is not integer division: `7 / 2` is `3.5`, and `-7 // 2` is `-4` because floor division rounds toward negative infinity. Do not confuse a number with its string form: `'3' * 4` is `'3333'`, not `12`.

## Worked example
```python
hours = 2
minutes = hours * 60
half = minutes / 2      # 60.0, a float
whole = minutes // 7    # 17, an int
```

minutes is 120. `/` gave a float and `//` gave a floored int, so pick the operator by the type the contract asks for.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```python
def total_cost(price, quantity):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def total_cost(price, quantity):
    return price * quantity
```
