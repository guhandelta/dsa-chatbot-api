---
track: language
language: javascript
level: beginner
order: 2
prerequisites: javascript-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: inRange
starter_code: "function inRange(value, low, high) {\n    // Write your solution here.\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# JavaScript: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition produces true or false. Combine conditions with && when both must hold, or || when either suffices. Boundary words such as inclusive determine whether comparisons use < or <=.

## Common misconception
A chained mathematical comparison does not translate directly into program syntax. Write both comparisons explicitly. JavaScript strict equality avoids coercion; Java compares primitive values with ==.

## Worked example
```javascript
const age = 18;
const canJoin = age >= 16 && age <= 25;
```

Both comparisons are true, so canJoin is true. Test each boundary independently when translating a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```javascript
function inRange(value, low, high) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. return value >= low && value <= high;

## Solutions
### JavaScript
```javascript
function inRange(value, low, high) {
    return value >= low && value <= high;
}
```
