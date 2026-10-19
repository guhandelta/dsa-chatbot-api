---
track: language
language: python
level: intermediate
order: 8
prerequisites: python-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: unique_count
starter_code: "def unique_count(values):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# Python: Sets and equality — Easy — Shared curriculum

## Learn
A set records membership and stores each distinct, hashable value once. Adding a duplicate does not grow it. Choose a set when you need uniqueness and a dict when each key also needs a value. `frozenset` is the immutable, hashable version.

## Common misconception
Lists and dicts are unhashable, so `{[1, 2]}` raises TypeError; use a tuple. Do not rely on set iteration order. `1`, `1.0` and `True` are equal and hash the same, so they collapse into one element.

## Worked example
```python
visited = set()
visited.add(7)
visited.add(7)
found = 7 in visited
```

found is True and len(visited) is 1: adding 7 twice stored it once.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```python
def unique_count(values):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def unique_count(values):
    return len(set(values))
```
