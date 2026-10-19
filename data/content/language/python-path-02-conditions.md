---
track: language
language: python
level: beginner
order: 2
prerequisites: python-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: in_range
starter_code: "def in_range(value, low, high):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# Python: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition produces `True` or `False`. Combine conditions with `and` when both must hold and `or` when either suffices. Python also allows a chained comparison such as `low <= value <= high`, which means `low <= value and value <= high`.

## Common misconception
Boundary words such as inclusive decide between `<` and `<=`. `and`/`or` return one of their operands, not always a bool: `0 or 5` is `5`. Use `==` for value equality and keep `is` for `None` checks.

## Worked example
```python
age = 18
can_join = 16 <= age <= 25
```

Both comparisons hold, so can_join is True. Test each boundary on its own when translating a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `True`

## Starter code
```python
def in_range(value, low, high):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def in_range(value, low, high):
    return low <= value <= high
```
