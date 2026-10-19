---
track: language
language: python
level: beginner
order: 5
prerequisites: python-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: count_vowels
starter_code: "def count_vowels(text):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# Python: Strings and iteration — Easy — Shared curriculum

## Learn
A string is an immutable, ordered sequence. Indices start at 0 and the last valid index is `len(text) - 1`; `text[-1]` counts from the end. Iterating with `for ch in text` visits each character without index arithmetic. This exercise restricts inputs to lowercase English letters.

## Common misconception
`text[len(text)]` raises IndexError, while a slice past the end such as `text[1:99]` quietly stops at the end. String methods return new strings: `text.upper()` does not change `text`.

## Worked example
```python
word = "cat"
first = word[0]
last = word[-1]
length = len(word)
```

first is 'c', last is 't' and length is 3. Valid positive indices are 0, 1 and 2.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```python
def count_vowels(text):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def count_vowels(text):
    return sum(1 for ch in text if ch in "aeiou")
```
