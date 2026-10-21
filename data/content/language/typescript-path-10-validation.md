---
track: language
language: typescript
level: intermediate
order: 10
prerequisites: typescript-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: safeAt
starter_code: "function safeAt(values: readonly number[], index: number, fallback: number): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# TypeScript: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data. Define the behavior for invalid input explicitly: a fallback value, a structured error, or an exception. This task chooses a fallback, making every input in the contract meaningful. In TypeScript the element read `values[index]` is typed `number` even when the index is out of range, so the compiler will not remind you to check; the compiler option `noUncheckedIndexedAccess` changes that read to `number | undefined`. The method `Array.prototype.at` is typed `number | undefined`.

## Common misconception
JavaScript does not throw for an invalid array index; it returns `undefined`, and `values[index]` is still typed `number`, so the wrong value flows on unnoticed. `values.at(index)` looks like a safe replacement but accepts negative indices that count from the end: `[2, 4].at(-1)` is 4, not a fallback. Validate negative indices as well as indices equal to or larger than the length. Catching every exception can conceal unrelated defects.

## Worked example
```typescript
function parsePort(text: string): number | null {
  const port = Number(text);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    return null;
  }
  return port;
}
```

`parsePort("8080")` is 8080; `parsePort("abc")`, `parsePort("")` and `parsePort("70000")` are `null`. The return type `number | null` makes the failure part of the contract, so callers must handle it. The exercise below deliberately chooses a numeric fallback instead, so do not copy the `null` return into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```typescript
function safeAt(values: readonly number[], index: number, fallback: number): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: check first whether the index is below 0 or at least `values.length`; if it is, return the fallback; otherwise return the element.

## Solutions
### TypeScript
```typescript
function safeAt(values: readonly number[], index: number, fallback: number): number {
    if (index < 0 || index >= values.length) {
        return fallback;
    }
    return values[index];
}
```
