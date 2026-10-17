---
track: language
language: javascript
level: intermediate
order: 6
prerequisites: javascript-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: countAbove
starter_code: "function countAbove(values, threshold) {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# JavaScript: Arrays and indexed collections — Easy — Shared curriculum

## Learn
An array stores an ordered collection accessed by index. Traversal visits each element once. Distinguish the index from the value at that index and distinguish a new copy from another reference to the same collection.

## Common misconception
Java arrays have fixed length and typed elements; JavaScript arrays can grow. In both languages, assigning one array variable to another does not copy its elements. Strictly greater excludes equal values.

## Worked example
```javascript
const scores = [3, 8];
const alias = scores;
alias[0] = 5;
```

scores[0] is now 5 because both variables refer to the same array. To preserve the original, create a separate collection before changing elements.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```javascript
function countAbove(values, threshold) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. int count = 0; for (int value : values) { if (value > threshold) { count++; } } return count;

## Solutions
### JavaScript
```javascript
function countAbove(values, threshold) {
    let count = 0; for (const value of values) { if (value > threshold) { count++; } } return count;
}
```
