---
track: language
language: typescript
level: intermediate
order: 6
prerequisites: typescript-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: countAbove
starter_code: "function countAbove(values: readonly number[], threshold: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# TypeScript: Arrays and lists — Easy — Shared curriculum

## Learn
An array stores an ordered collection accessed by index. Traversal visits each element once. Distinguish the index from the value at that index, and distinguish a new copy from another reference to the same array. TypeScript writes the element type in the annotation: `number[]` for an array that may be changed and `readonly number[]` for a view that hides `push`, `sort` and the other mutating methods. A parameter typed `readonly number[]` promises the caller that the function will not change the array, and a mutable array can be passed where a readonly one is expected. Contract here: do not modify the argument.

## Common misconception
Strictly greater excludes equal values. The compiler types `values[i]` as `number` for any index, even one past the end, because it does not track the array's length; at run time that read is `undefined`, and `undefined > threshold` is `false`, so a loop bound of `i <= values.length` can hide inside a counting loop. Assigning one array variable to another does not copy its elements. `readonly` is a compile-time view: it does not freeze the array.

## Worked example
```typescript
const scores: number[] = [3, 8];
const alias: number[] = scores;
alias[0] = 5;
const view: readonly number[] = scores;
```

`scores[0]` is now 5 because both variables refer to the same array. `view` also refers to it, but through a type without mutating methods, so `view.push(1)` is a compile error while `scores` still sees any change made through `alias`. To keep the original unchanged, create a separate array before changing elements.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```typescript
function countAbove(values: readonly number[], threshold: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: traverse the array once, compare each element with the threshold using a strict `>`, and count the matches. The argument is `readonly`, so the compiler also stops you from changing it.

## Solutions
### TypeScript
```typescript
function countAbove(values: readonly number[], threshold: number): number {
    let count = 0;
    for (const value of values) {
        if (value > threshold) {
            count++;
        }
    }
    return count;
}
```
