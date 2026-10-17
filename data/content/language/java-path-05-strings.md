---
track: language
language: java
level: beginner
order: 5
prerequisites: java-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_java: countVowels
starter_code: "public int countVowels(String text) {\n    // Write your solution here.\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# Java: Strings and iteration — Easy — Shared curriculum

## Learn
A string is an ordered sequence. Indices start at zero and stop before its length. Strings are immutable; inspecting a character does not modify the original. The definition of character matters: this exercise deliberately restricts inputs to lowercase English letters.

## Common misconception
Do not read index length: the final valid index is length - 1. Java uses length() and charAt(i); JavaScript uses length and text[i]. Unicode outside this contract needs a more careful definition than a UTF-16 code unit.

## Worked example
```java
String word = "cat";
char first = word.charAt(0);
int length = word.length();
```

The first character is c and the length is 3. Valid indices are 0, 1, and 2. In Java, single quotes describe a char while double quotes describe a String.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```java
public int countVowels(String text) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. int count = 0; for (int i = 0; i < text.length(); i++) { if ("aeiou".indexOf(text.charAt(i)) >= 0) { count++; } } return count;

## Solutions
### Java
```java
public int countVowels(String text) {
    int count = 0; for (int i = 0; i < text.length(); i++) { if ("aeiou".indexOf(text.charAt(i)) >= 0) { count++; } } return count;
}
```
