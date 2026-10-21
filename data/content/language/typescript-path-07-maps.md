---
track: language
language: typescript
level: intermediate
order: 7
prerequisites: typescript-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: countTarget
starter_code: "function countTarget(words: readonly string[], target: string): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# TypeScript: Maps and frequency counting — Easy — Shared curriculum

## Learn
A map associates a key with a value. A frequency map maintains how many times each key has appeared. TypeScript writes both types in the declaration: `Map<string, number>` maps `string` keys to `number` counts. `get(key)` returns `V | undefined`, because the key may be missing, so reading a missing key needs an explicit default before it can be used as a number; `??` supplies a value only when the left side is `undefined` or `null`. `has(key)` reports whether a key is present. Keys and values play different roles.

## Common misconception
Do not assume every queried word has appeared. `counts.get(word) + 1` does not compile (the compiler reports that the value is possibly undefined), which is the compiler catching exactly this mistake. Silencing it with `!` or `as number` removes the error but not the problem: for a missing key the expression is `undefined + 1`, which is `NaN` at run time. Give the lookup a default with `??` instead.

## Worked example
```typescript
const ages = new Map<string, number>();
ages.set("Ada", 30);
const known: boolean = ages.has("Ada");
const bob: number | undefined = ages.get("Bob");
```

`known` is `true`. Ada is the key and 30 is the associated value. `bob` is `undefined`, and its type says so: the annotation `number | undefined` is what `get` returns, so the compiler forces any arithmetic on it to handle the missing case first.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```typescript
function countTarget(words: readonly string[], target: string): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: walk the words once, storing for each word its previous count (or 0 when absent) plus one in a `Map<string, number>`. Afterwards look up the target with a default of 0, because the target may never have appeared.

## Solutions
### TypeScript
```typescript
function countTarget(words: readonly string[], target: string): number {
    const counts = new Map<string, number>();
    for (const word of words) {
        counts.set(word, (counts.get(word) ?? 0) + 1);
    }
    return counts.get(target) ?? 0;
}
```
