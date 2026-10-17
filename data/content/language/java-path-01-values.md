---
track: language
language: java
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_java: totalCost
starter_code: "public int totalCost(int price, int quantity) {\n    // Write your solution here.\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# Java: Values and arithmetic — Easy — Shared curriculum

## Learn
Expressions combine values into a new value. Choose a type that can represent the inputs and result; a variable name describes what a value means. A function returns its result to the caller rather than printing it.

## Common misconception
Do not confuse a numeric value with its string representation. JavaScript + can concatenate strings; use the numeric inputs supplied here. Java uses declared numeric types and integer arithmetic.

## Worked example
```java
int hours = 2;
int minutes = hours * 60;
```

minutes is 120. Multiplication creates a number; assigning it stores that value under a descriptive name.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```java
public int totalCost(int price, int quantity) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. return price * quantity;

## Solutions
### Java
```java
public int totalCost(int price, int quantity) {
    return price * quantity;
}
```
