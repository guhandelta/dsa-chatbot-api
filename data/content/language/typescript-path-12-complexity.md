---
track: language
language: typescript
level: expert
order: 12
prerequisites: typescript-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: hasPair
starter_code: "function hasPair(values: readonly number[], target: number): boolean {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# TypeScript: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. Types are erased, so TypeScript annotations cost nothing at run time: the cost of `Set<number>` is the cost of a JavaScript `Set`. A single traversal with average constant-time `has` and `add` has expected linear time; two nested traversals over the same array take quadratic time. An invariant states what is true about the data structure before each iteration. Contract here: the two elements must be at different indices, and the answer is a `boolean`.

## Common misconception
Two different indices may hold the same value, and one index must never be used twice: `[1, 1]` with target 2 is `true`, but `[1]` with target 2 is `false`. Never reuse the current element as its own partner. The compiler cannot help here, because it types every `values[i]` as `number` and knows nothing about which indices you have already used. A correct result on six tests is evidence, not a proof; explain your invariant and complexity as part of your mastery check.

## Worked example
```typescript
const values: number[] = [4, 7, 9];
let visits = 0;
for (const value of values) {
  visits += 1;
}
```

`visits` is 3: one visit per element, so n visits for n elements. Nesting a complete second traversal inside each visit creates n × n visits. Always count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```typescript
function hasPair(values: readonly number[], target: number): boolean {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: keep a `Set<number>` of values already visited. For each value, check whether the set contains `target - value` before adding the value itself; that ordering guarantees the partner sits at a different index.

## Solutions
### TypeScript
```typescript
function hasPair(values: readonly number[], target: number): boolean {
    const seen = new Set<number>();
    for (const value of values) {
        if (seen.has(target - value)) {
            return true;
        }
        seen.add(value);
    }
    return false;
}
```
