---
track: language
language: python
level: intermediate
order: 10
prerequisites: python-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: safe_at
starter_code: "def safe_at(values, index, fallback):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# Python: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define what invalid input does: a fallback value, a structured error or an exception. This task chooses a fallback, so every input in the contract has a meaningful result.

## Common misconception
Python accepts negative indices, so `values[-1]` silently returns the last element instead of failing; check `0 <= index < len(values)` explicitly. A bare `except:` can hide unrelated defects.

## Worked example
```python
def positive(value):
    if value <= 0:
        raise ValueError("Expected a positive value")
    return value
```

positive(3) returns 3 and positive(0) raises. That is one failure contract; the exercise below chooses a fallback instead, so do not copy the exception.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```python
def safe_at(values, index, fallback):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def safe_at(values, index, fallback):
    if 0 <= index < len(values):
        return values[index]
    return fallback
```
