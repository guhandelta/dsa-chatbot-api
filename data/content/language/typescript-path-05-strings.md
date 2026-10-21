---
track: language
language: typescript
level: beginner
order: 5
prerequisites: typescript-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: countVowels
starter_code: "function countVowels(text: string): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# TypeScript: Strings and iteration — Easy — Shared curriculum

## Learn
A string is an ordered sequence. Indices start at zero and stop before its `length`. Strings are immutable; inspecting a character does not modify the original. At run time a TypeScript `string` is a JavaScript string: a sequence of UTF-16 code units, so `length` counts code units, not user-perceived characters. `text[i]` has type `string`, and `for (const ch of text)` visits one code point at a time. This exercise deliberately restricts inputs to lowercase English letters, where code units and characters coincide.

## Common misconception
Do not read index `length`: the final valid index is `length - 1`, and reading past it gives `undefined` at run time even though the compiler types `text[i]` as `string`. Do not assume `length` counts characters either: `"😀".length` is 2, while `[..."😀"].length` is 1. Unicode outside this contract needs a more careful definition than a UTF-16 code unit.

## Worked example
```typescript
const word: string = "cat";
const first: string = word[0];
const size: number = word.length;
```

`first` is `"c"` and `size` is 3. Valid indices are 0, 1 and 2. A single character is still a `string`: TypeScript has no separate `char` type.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```typescript
function countVowels(text: string): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: visit each character of the string once, test whether it is one of the five vowels, and increment a counter when it is. Return the counter; an empty string returns 0.

## Solutions
### TypeScript
```typescript
function countVowels(text: string): number {
    let count = 0;
    for (const ch of text) {
        if ("aeiou".includes(ch)) {
            count++;
        }
    }
    return count;
}
```
