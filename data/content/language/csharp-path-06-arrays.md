---
track: language
language: csharp
level: intermediate
order: 6
prerequisites: csharp-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: CountAbove
starter_code: "public static class Solution\n{\n    public static long CountAbove(long[] values, long threshold)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# C#: Arrays and lists — Easy — Shared curriculum

## Learn
An array stores a fixed number of elements accessed by zero-based index; `Length` is its size. Arrays are reference types even when their elements are value types, so an array variable holds a reference to the array object. Traversal visits each element once. Distinguish the index from the value at that index, and distinguish a new copy from another reference to the same array.

## Common misconception
`int[] b = a;` copies the reference, not the elements: after `b[0] = 9;`, `a[0]` is 9 too. Use `a.Clone()` (cast back to `int[]`), `ToArray()` or `Array.Copy` for an independent copy; clones are shallow, so an array of objects copies references to the same objects. `a == c` compares two arrays by reference, not by contents. Strictly greater excludes equal values.

## Worked example
```csharp
long[] scores = { 3, 8 };
long[] alias = scores;
alias[0] = 5;
long[] copy = (long[])scores.Clone();
copy[1] = 0;
```

scores[0] is now 5 because alias refers to the same array, and scores[1] is still 8 because copy is a separate array.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000, passed as `long`. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```csharp
public static class Solution
{
    public static long CountAbove(long[] values, long threshold)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Traverse the array once without changing it, test each element against the threshold with a strict comparison, and count the matches. Trace the empty array and an element equal to the threshold.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long CountAbove(long[] values, long threshold)
    {
        long count = 0;
        foreach (long value in values)
        {
            if (value > threshold)
            {
                count++;
            }
        }
        return count;
    }
}
```
