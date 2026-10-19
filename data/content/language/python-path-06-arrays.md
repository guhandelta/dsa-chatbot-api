---
track: language
language: python
level: intermediate
order: 6
prerequisites: python-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: count_above
starter_code: "def count_above(values, threshold):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# Python: Lists and indexed collections — Easy — Shared curriculum

## Learn
A list stores an ordered, growable collection accessed by index. Assigning a list to another name does not copy it, while slicing (`values[:]`) makes a shallow copy. Distinguish an index from the value stored there.

## Common misconception
`[[0] * 3] * 2` repeats one inner list twice, so changing one row changes both; build rows with a comprehension. Strictly greater excludes equal values. Do not modify `values`.

## Worked example
```python
scores = [3, 8]
alias = scores
copy = scores[:]
alias[0] = 5
```

scores[0] is now 5 because `alias` names the same list, but `copy[0]` is still 3 because slicing made a new list.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```python
def count_above(values, threshold):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def count_above(values, threshold):
    return sum(1 for value in values if value > threshold)
```
