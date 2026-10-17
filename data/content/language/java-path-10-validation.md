---
track: language
language: java
level: intermediate
order: 10
prerequisites: java-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_java: safeAt
starter_code: "public int safeAt(int[] values, int index, int fallback) {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# Java: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data. Define the behavior for invalid input explicitly: a fallback value, a structured error, or an exception. This task chooses a fallback, making every input in the contract meaningful.

## Common misconception
Java throws for invalid array access while JavaScript usually returns undefined. Neither behavior satisfies this task. Validate negative indices as well as indices equal to or larger than the length. Catching every exception can conceal unrelated defects.

## Worked example
```java
int positive(int value) {
  if (value <= 0) {
    throw new IllegalArgumentException("Expected a positive value");
  }
  return value;
}
```

Calling this helper with 3 returns 3; calling it with 0 throws. That is one failure contract. The exercise below deliberately chooses a fallback instead, so do not copy the exception behavior into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```java
public int safeAt(int[] values, int index, int fallback) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. if (index < 0 || index >= values.length) { return fallback; } return values[index];

## Solutions
### Java
```java
public int safeAt(int[] values, int index, int fallback) {
    if (index < 0 || index >= values.length) { return fallback; } return values[index];
}
```
