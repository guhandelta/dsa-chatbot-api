---
track: language
language: typescript
level: intermediate
order: 8
prerequisites: typescript-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: uniqueCount
starter_code: "function uniqueCount(values: readonly number[]): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# TypeScript: Sets and equality — Easy — Shared curriculum

## Learn
A set records membership and stores each distinct key once. Adding a duplicate does not increase its size. Choose a set when you need uniqueness, and a map when each key also needs an associated value. `Set<number>` stores numbers; you can build one from an array, and its element count is the property `size`. A set iterates in insertion order, but do not depend on order for the answer here. Keys are compared with SameValueZero equality: numbers and strings by value, objects by reference.

## Common misconception
A set has `size`, not `length`: `seen.length` does not compile (TS2339), and in plain JavaScript it silently gives `undefined`. Equal-looking objects are different keys, so `new Set([{ a: 1 }, { a: 1 }]).size` is 2. These are numbers, so equal values are the same key. Do not depend on iteration order from a set; only its membership matters here.

## Worked example
```typescript
const tags = new Set<string>();
tags.add("a");
tags.add("a");
tags.add("b");
```

`tags.size` is 2 and `tags.has("a")` is `true`. Adding the same string twice does not create two entries, and nothing about the order of the calls changes which entries exist.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```typescript
function uniqueCount(values: readonly number[]): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: build a `Set<number>` from the array so duplicates collapse, and return its `size`.

## Solutions
### TypeScript
```typescript
function uniqueCount(values: readonly number[]): number {
    const seen = new Set<number>(values);
    return seen.size;
}
```
