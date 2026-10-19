---
track: language
language: python
level: expert
order: 12
prerequisites: python-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: has_pair
starter_code: "def has_pair(values, target):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# Python: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes extra storage. A single pass with average O(1) set operations is expected O(n). `x in a_list` is O(n) but `x in a_set` is O(1) on average, and `list.pop(0)` is O(n) while `deque.popleft()` is O(1).

## Common misconception
Two different indices may hold the same value; never reuse the current element as its own partner. Passing six tests is evidence, not a proof: explain your invariant and complexity as part of the mastery check.

## Worked example
```python
values = [4, 7, 9]
for value in values:
    pass  # one visit per element
```

There are n visits for n elements. Nesting a full second loop inside creates n * n visits. Count how often operations run, not how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `False`

## Starter code
```python
def has_pair(values, target):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def has_pair(values, target):
    seen = set()
    for value in values:
        if target - value in seen:
            return True
        seen.add(value)
    return False
```
