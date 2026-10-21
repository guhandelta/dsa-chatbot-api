---
track: language
language: typescript
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: totalCost
starter_code: "function totalCost(price: number, quantity: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# TypeScript: Values and arithmetic — Easy — Shared curriculum

## Learn
Expressions combine values into a new value, and in TypeScript every value has a static type. Arithmetic works on `number`, which is one IEEE-754 double: there is no separate integer type, so the annotation `number` describes `3` and `3.5` alike, and whole numbers are exact only up to `Number.MAX_SAFE_INTEGER` (2^53 - 1). A function declares its parameter types and its return type; the compiler checks every call and the returned expression against them, and then erases the annotations. A function returns its result to the caller rather than printing it. Contract here: two whole numbers in, one whole number out, and a zero in either input gives zero.

## Common misconception
`number` is not an integer type. The compiler accepts `0.1 + 0.2`, and the result is `0.30000000000000004`, not `0.3`. A type annotation is also not a runtime check: it is erased, so a value that enters through `JSON.parse` (typed `any`) can be a string at run time, and then `+` concatenates instead of adding (`"5" + 1` is `"51"`). In this exercise both inputs are whole numbers from 0 to 1000, so every result is exact.

## Worked example
```typescript
const hours: number = 2;
const minutes: number = hours * 60;
const label: string = `${minutes} min`;
```

`minutes` is 120 and `label` is `"120 min"`. Both `hours` and `minutes` have type `number`; the template literal turns a number into a `string`, which is a different type. Naming a value by what it means keeps the arithmetic readable.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000. The result is at most 1000000, so it is exact in a `number`.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```typescript
function totalCost(price: number, quantity: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: the cost is the two parameters combined with the `*` operator, returned as a `number`. Check a zero input, which must give 0.

## Solutions
### TypeScript
```typescript
function totalCost(price: number, quantity: number): number {
    return price * quantity;
}
```
