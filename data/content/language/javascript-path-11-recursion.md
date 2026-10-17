---
track: language
language: javascript
level: expert
order: 11
prerequisites: javascript-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: digitSum
starter_code: "function digitSum(n) {\n    // Write your solution here.\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# JavaScript: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case supplies an answer without another call. A decreasing measure explains termination, and each call has its own local variables and return point.

## Common misconception
Check that the recursive input strictly approaches the base case. The result of a recursive call must contribute to the returned value. This small input bound keeps call depth modest; deeply recursive problems may need an explicit stack.

## Worked example
```javascript
function countdown(n) {
  if (n === 0) return 0;
  return countdown(n - 1);
}
```

For n = 2, the calls are countdown(2), countdown(1), countdown(0). The base case returns zero, which flows back through both callers. This example assumes n is nonnegative.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```javascript
function digitSum(n) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. if (n < 10) { return n; } return n % 10 + digitSum(n / 10);

## Solutions
### JavaScript
```javascript
function digitSum(n) {
    if (n < 10) { return n; } return n % 10 + digitSum(Math.floor(n / 10));
}
```
