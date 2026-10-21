---
track: language
language: typescript
level: beginner
order: 3
prerequisites: typescript-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: sumThrough
starter_code: "function sumThrough(n: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# TypeScript: Loops and accumulation — Easy — Shared curriculum

## Learn
A loop repeats a body while its condition holds. An accumulator stores the result of processing everything visited so far; state what it means before and after each iteration. In TypeScript the accumulator's type is inferred from its initial value, so `let total = 0` declares a `number` and the compiler then rejects assigning anything else to it. The three parts of `for (let i = 1; i <= n; i++)` are initialization, condition and update; the condition is checked before every iteration, including the first. Contract here: n is a whole number, and for n = 0 the loop body never runs.

## Common misconception
An off-by-one error changes which values are visited: `i < n` stops one short, and a loop that starts at 0 instead of 1 visits a value the task does not include. Trace n = 0 and n = 1 by hand through initialization, condition, update and return. Declare the accumulator outside the loop so it survives each iteration. Because its type comes from its initial value, `let total = 0; total += "1";` is a compile error (TS2322), which catches a mixed-up accumulator before the code runs.

## Worked example
```typescript
let evens = 0;
for (let i = 1; i <= 6; i++) {
  if (i % 2 === 0) {
    evens += 1;
  }
}
```

`evens` is 0 before the loop and becomes 1, 2, then 3 when `i` is 2, 4 and 6. Before each iteration it counts the even numbers among the integers already visited. Starting it at 1 instead of 0 would make every answer one too high.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```typescript
function sumThrough(n: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: start an accumulator at 0, loop `i` from 1 up to and including `n`, add `i` each time, and return the accumulator. For n = 0 the condition fails immediately and the initial 0 is returned.

## Solutions
### TypeScript
```typescript
function sumThrough(n: number): number {
    let total = 0;
    for (let i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}
```
