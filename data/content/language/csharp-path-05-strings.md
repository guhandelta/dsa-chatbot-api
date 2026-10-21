---
track: language
language: csharp
level: beginner
order: 5
prerequisites: csharp-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: CountVowels
starter_code: "public static class Solution\n{\n    public static long CountVowels(string text)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# C#: Strings and iteration — Easy — Shared curriculum

## Learn
A `string` is an immutable sequence of UTF-16 code units. `text[i]` returns a `char` (zero-based, valid indices 0 to `text.Length - 1`) and never modifies the string; `foreach (char c in text)` visits every code unit. `s += x` creates a new string each time, so build long results with `StringBuilder`. `==` on strings compares contents ordinally. This exercise restricts inputs to lowercase English letters, so every character is one code unit.

## Common misconception
Do not read index `Length`: the last valid index is `Length - 1`, and `"abc"[3]` throws `IndexOutOfRangeException`. `Length` counts UTF-16 code units, not visible characters, so `"\U0001F600".Length` is 2 for one emoji; this exercise avoids that by restricting its input. Single quotes make a `char` ('a') and double quotes make a `string` ("a").

## Worked example
```csharp
string word = "cat";
char first = word[0];
int length = word.Length;
char last = word[^1];
```

first is 'c', length is 3 and last is 't'. Valid indices are 0, 1 and 2, and `word[^1]` counts from the end.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count as a `long`.

## Example
Arguments: `[""]` → `0`

## Starter code
```csharp
public static class Solution
{
    public static long CountVowels(string text)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Visit every character of text once. Decide, for each character, whether it is one of the five vowels and count it if so. Trace the empty string and a word with no vowels.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long CountVowels(string text)
    {
        long count = 0;
        foreach (char ch in text)
        {
            if ("aeiou".Contains(ch))
            {
                count++;
            }
        }
        return count;
    }
}
```
