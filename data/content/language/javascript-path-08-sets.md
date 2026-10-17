---
track: language
language: javascript
level: intermediate
order: 8
prerequisites: javascript-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: uniqueCount
starter_code: "function uniqueCount(values) {\n    // Write your solution here.\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# JavaScript: Sets and equality — Easy — Shared curriculum

## Learn
A set records membership and stores each distinct key once. Adding a duplicate does not increase its size. Choose a set when you need uniqueness, and a map when each key also needs an associated value.

## Common misconception
Do not depend on iteration order from a hash set. Java boxes primitive integers in HashSet<Integer>; JavaScript Set stores numeric primitives directly. Equality of object keys differs from equality of these primitive numbers.

## Worked example
```javascript
const visited = new Set();
visited.add(7);
visited.add(7);
const found = visited.has(7);
```

Membership is true and the set has one element. Adding the same numeric key twice does not create two entries.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```javascript
function uniqueCount(values) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. Set<Integer> seen = new HashSet<>(); for (int value : values) { seen.add(value); } return seen.size();

## Solutions
### JavaScript
```javascript
function uniqueCount(values) {
    const seen = new Set(values); return seen.size;
}
```
