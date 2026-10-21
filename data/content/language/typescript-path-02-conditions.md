---
track: language
language: typescript
level: beginner
order: 2
prerequisites: typescript-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: inRange
starter_code: "function inRange(value: number, low: number, high: number): boolean {\n    // Write your solution here.\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# TypeScript: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition has type `boolean`. Comparison operators such as `<`, `<=`, `>` and `>=` take two numbers and produce a `boolean`; combine conditions with `&&` when both must hold or `||` when either suffices. Both operators stop as soon as the answer is known. Boundary words such as inclusive decide whether a comparison uses `<` or `<=`. A function declared to return `boolean` must return `true` or `false`, not a number. Contract here: three integers in, one `boolean` out.

## Common misconception
A chained mathematical comparison does not translate into program syntax: `low <= value <= high` first evaluates `low <= value` to a `boolean`, then compares that `boolean` with `high`. TypeScript rejects it (error TS2365: Operator '<=' cannot be applied to types 'boolean' and 'number'). Plain JavaScript runs it silently, treating `true` as 1, so for `value = 9, low = 1, high = 5` it wrongly evaluates to `true`. Write both comparisons explicitly and test each boundary on its own.

## Worked example
```typescript
const age: number = 18;
const canJoin: boolean = age >= 16 && age <= 25;
```

Both comparisons are true, so `canJoin` is `true`. The expression is a `boolean`, which is exactly what the annotation promises. Test each boundary independently when translating a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```typescript
function inRange(value: number, low: number, high: number): boolean {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: one comparison for the lower boundary and one for the upper boundary, joined with `&&`, and return the resulting `boolean` directly.

## Solutions
### TypeScript
```typescript
function inRange(value: number, low: number, high: number): boolean {
    return value >= low && value <= high;
}
```
