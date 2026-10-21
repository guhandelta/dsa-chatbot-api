---
track: language
language: typescript
level: expert
order: 11
prerequisites: typescript-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: digitSum
starter_code: "function digitSum(n: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# TypeScript: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case supplies an answer without another call. A decreasing measure explains termination, and each call has its own local variables and return point. TypeScript adds no stack of its own: depth is limited by the JavaScript engine that runs the output. Give a recursive function an explicit return type; without one, the compiler cannot infer the type from a body that calls itself and, under `noImplicitAny`, reports error TS7023. Contract here: n is a nonnegative whole number.

## Common misconception
Check that the recursive input strictly approaches the base case, and that it is still a whole number. `/` on `number` is floating-point division: `123 / 10` is 12.3, not 12, so passing `n / 10` to the recursive call computes a wrong sum (about 6.53 for 123). Use `Math.floor` (or `Math.trunc`) for integer division. The result of a recursive call must contribute to the returned value. This small input bound keeps call depth modest; deeply recursive problems may need an explicit stack.

## Worked example
```typescript
function sumTo(n: number): number {
  if (n === 0) return 0;
  return n + sumTo(n - 1);
}
```

For n = 2 the calls are `sumTo(2)`, `sumTo(1)`, `sumTo(0)`. The base case returns 0, which flows back through both callers to give 1 and then 3. The explicit `: number` return annotation is required because `sumTo` appears in its own return expression. This example assumes n is a nonnegative whole number.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```typescript
function digitSum(n: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: if `n` has a single digit, return it; otherwise return its last digit (`n % 10`) plus the digit sum of the number with the last digit removed, computed with integer division.

## Solutions
### TypeScript
```typescript
function digitSum(n: number): number {
    if (n < 10) {
        return n;
    }
    return (n % 10) + digitSum(Math.floor(n / 10));
}
```
