---
track: language
language: java
level: expert
order: 12
prerequisites: java-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_java: hasPair
starter_code: "public boolean hasPair(int[] values, int target) {\n    // Write your solution here.\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# Java: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. A single traversal with average constant-time set operations has expected linear time. An invariant states what is true about the data structure before each iteration.

## Common misconception
Two different indices may hold the same value. Never reuse the current element as its own partner. A correct result on six tests is evidence, not a proof; explain your invariant and complexity as part of your mastery check.

## Worked example
```java
int[] values = {4, 7, 9};
for (int value : values) {
  // One visit per element.
}
```

There are n visits for n elements. Nesting a complete second traversal inside each visit creates n × n visits. Always count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```java
public boolean hasPair(int[] values, int target) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. Set<Integer> seen = new HashSet<>(); for (int value : values) { if (seen.contains(target - value)) { return true; } seen.add(value); } return false;

## Solutions
### Java
```java
public boolean hasPair(int[] values, int target) {
    Set<Integer> seen = new HashSet<>(); for (int value : values) { if (seen.contains(target - value)) { return true; } seen.add(value); } return false;
}
```
