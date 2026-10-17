---
track: language
language: java
level: beginner
order: 4
prerequisites: java-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_java: distance
starter_code: "public int distance(int a, int b) {\n    // Write your solution here.\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# Java: Functions and contracts — Easy — Shared curriculum

## Learn
A function contract describes arguments, return values, and valid inputs. Parameters are local names for arguments. A return ends the current call; printing does not satisfy a return-value contract. Small functions are easiest to verify when they have one purpose.

## Common misconception
Keep the function name and argument order unchanged because another program calls them. Negative positions still have a nonnegative distance. A function should work on every valid call, not only the example.

## Worked example
```java
int doubleValue(int value) {
  return value * 2;
}
// Inside another method: int result = doubleValue(4);
```

The argument 4 becomes the parameter value for this call, and the returned result is 8. A second call gets its own parameter value. The exercise runner calls your supplied function or method; you do not need a main program.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```java
public int distance(int a, int b) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. return Math.abs(a - b);

## Solutions
### Java
```java
public int distance(int a, int b) {
    return Math.abs(a - b);
}
```
