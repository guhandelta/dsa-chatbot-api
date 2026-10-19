---
track: language
language: python
level: beginner
order: 4
prerequisites: python-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: distance
starter_code: "def distance(a, b):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# Python: Functions and contracts — Easy — Shared curriculum

## Learn
A function contract describes its arguments, return value and valid inputs. Parameters are local names for the arguments of one call. `return` ends the call; printing does not satisfy a return-value contract. Python binds default argument values once, when `def` runs.

## Common misconception
A mutable default such as `def add(x, items=[])` is shared by every call that omits `items`, so state leaks between calls; use `items=None` and create the list inside. Keep the function name and argument order unchanged because the runner calls them.

## Worked example
```python
def double(value):
    return value * 2

result = double(4)
```

The argument 4 becomes `value` for this call and 8 is returned. A second call gets its own `value`. The exercise runner calls your function; you do not need a main program.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```python
def distance(a, b):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def distance(a, b):
    return abs(a - b)
```
