---
track: language
language: csharp
level: expert
order: 12
prerequisites: csharp-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: HasPair
starter_code: "using System.Collections.Generic;\n\npublic static class Solution\n{\n    public static bool HasPair(long[] values, long target)\n    {\n        // Write your solution here.\n        return false;\n    }\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# C#: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. A single traversal with expected O(1) `HashSet` operations has expected linear time, while a `List<T>.Contains` inside a loop is O(n) per call and makes the whole algorithm quadratic. An invariant states what is true about the data structure before each iteration.

## Common misconception
Two different indices may hold the same value, but one index must never be its own partner: if you add the current element to the set before checking for its complement, `[1]` with target 2 wrongly succeeds. A correct result on six tests is evidence, not a proof: the tests would also pass code that only checks neighbouring elements, only pairs with the first element, or ignores a negative second element. Trace `[9, 2, 5, 8]` with target 10 (the pair is not adjacent and does not use index 0) and `[6, -4]` with target 2 (the second element is negative) yourself, and explain your invariant and complexity as part of your mastery check.

## Worked example
```csharp
int[] values = { 4, 7, 9 };
int visits = 0;
foreach (int value in values)
{
    visits++;
}
int pairs = 0;
foreach (int a in values)
{
    foreach (int b in values)
    {
        pairs++;
    }
}
```

visits is 3 and pairs is 9: one visit per element for n elements, and n times n visits when a complete second traversal is nested inside each visit. Always count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000, passed as `long`.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static bool HasPair(long[] values, long target)
    {
        // Write your solution here.
        return false;
    }
}
```

## Approach
Scan once, remembering the elements seen so far in a set. For each element, ask whether its complement (target minus the element) was already seen before this element was added. State the invariant about the set before each iteration, and the time and space cost.

## Solutions
### C#
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static bool HasPair(long[] values, long target)
    {
        var seen = new HashSet<long>();
        foreach (long value in values)
        {
            if (seen.Contains(target - value))
            {
                return true;
            }
            seen.Add(value);
        }
        return false;
    }
}
```
