---
track: language
language: javascript
level: beginner
order: 3
prerequisites: javascript-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: sumThrough
starter_code: "function sumThrough(n) {\n    // Write your solution here.\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# JavaScript: Loops and accumulation — Easy — Shared curriculum

## Learn
A loop repeats a body while its condition holds. An accumulator stores the result of processing everything visited so far. State what that accumulator means before and after each iteration.

## Common misconception
An off-by-one error changes which values are visited. Check n = 0 and n = 1 by tracing initialization, condition, update, and return. Declare the accumulator outside the loop so it survives each iteration.

## Worked example
```javascript
let product = 1;
for (let i = 1; i <= 3; i++) {
  product *= i;
}
```

product changes from 1 to 1, then 2, then 6. Before each iteration it is the product of the previously visited integers. Changing the initial value to zero would make every result zero.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```javascript
function sumThrough(n) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. int total = 0; for (int i = 1; i <= n; i++) { total += i; } return total;

## Solutions
### JavaScript
```javascript
function sumThrough(n) {
    let total = 0; for (let i = 1; i <= n; i++) { total += i; } return total;
}
```
