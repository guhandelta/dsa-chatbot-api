---
track: language
language: javascript
level: intermediate
order: 7
prerequisites: javascript-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: countTarget
starter_code: "function countTarget(words, target) {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# JavaScript: Maps and frequency counting — Easy — Shared curriculum

## Learn
A map associates a key with a value. A frequency map maintains how many times each key has appeared. Reading a missing key needs an explicit default before incrementing its count. Keys and values play different roles.

## Common misconception
Java uses HashMap<String, Integer> and getOrDefault; compare strings by value rather than ==. JavaScript Map uses get and set; get on a missing key returns undefined. Do not assume every queried word has appeared.

## Worked example
```javascript
const ages = new Map();
ages.set("Ada", 30);
const known = ages.has("Ada");
```

known is true. Ada is the key and 30 is the associated value. Java collection examples use import java.util.*; the exercise runner supplies that import for bare methods.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```javascript
function countTarget(words, target) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. Map<String, Integer> counts = new HashMap<>(); for (String word : words) { counts.put(word, counts.getOrDefault(word, 0) + 1); } return counts.getOrDefault(target, 0);

## Solutions
### JavaScript
```javascript
function countTarget(words, target) {
    const counts = new Map(); for (const word of words) { counts.set(word, (counts.get(word) ?? 0) + 1); } return counts.get(target) ?? 0;
}
```
