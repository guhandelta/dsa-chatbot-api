---
track: language
language: python
level: intermediate
order: 7
prerequisites: python-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: count_target
starter_code: "def count_target(words, target):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# Python: Dicts and frequency counting — Easy — Shared curriculum

## Learn
A dict associates each key with a value and keeps insertion order. A frequency map stores how many times each key has appeared. `counts.get(word, 0)` supplies a default for a missing key; `collections.Counter` and `defaultdict(int)` package the same idea.

## Common misconception
`counts[word] += 1` raises KeyError the first time a plain dict sees `word`. Reading a missing key from a `defaultdict` silently inserts it, which changes `len(counts)`. Do not assume every queried word has appeared.

## Worked example
```python
ages = {}
ages["Ada"] = 30
known = "Ada" in ages
missing = ages.get("Grace", 0)
```

known is True and missing is 0. Ada is the key and 30 the associated value; `get` read a default without inserting Grace.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency dict as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```python
def count_target(words, target):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def count_target(words, target):
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts.get(target, 0)
```
