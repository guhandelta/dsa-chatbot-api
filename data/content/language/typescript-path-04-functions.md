---
track: language
language: typescript
level: beginner
order: 4
prerequisites: typescript-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: distance
starter_code: "function distance(a: number, b: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# TypeScript: Functions and contracts — Easy — Shared curriculum

## Learn
A function contract describes arguments, return values and valid inputs. In TypeScript the signature carries part of that contract: each parameter has a type, and the return type says what a caller receives. The compiler checks that every call passes the right number of arguments of the right types (calling a two-parameter function with one argument is error TS2554), and that every `return` matches the declared return type. Parameters are local names for arguments. A return ends the current call; printing does not satisfy a return-value contract. Small functions with one purpose are easiest to verify.

## Common misconception
Keep the function name and argument order unchanged because the runner calls it by name. Negative positions still have a nonnegative distance, and `a - b` is negative when `b` is larger. The signature is checked only at compile time: annotations are erased, so data that arrives through `any` (for example from `JSON.parse`) can still pass `undefined` at run time and produce `NaN`. A function should work on every valid call, not only on the example.

## Worked example
```typescript
function half(value: number): number {
  return value / 2;
}
const result: number = half(9);
```

The argument 9 becomes the parameter `value` for this call, and `result` is 4.5, because `/` is floating-point division and `number` has no integer type. A second call gets its own `value`. The exercise runner calls your supplied function; you do not need a main program.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```typescript
function distance(a: number, b: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: take the difference of the two positions and return its absolute value with `Math.abs`, so the order of `a` and `b` does not matter.

## Solutions
### TypeScript
```typescript
function distance(a: number, b: number): number {
    return Math.abs(a - b);
}
```
