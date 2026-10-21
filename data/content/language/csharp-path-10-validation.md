---
track: language
language: csharp
level: intermediate
order: 10
prerequisites: csharp-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: SafeAt
starter_code: "public static class Solution\n{\n    public static long SafeAt(long[] values, long index, long fallback)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# C#: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define the behaviour for invalid input explicitly: a fallback value, a `Try` method returning `bool`, or an exception. .NET code throws the most specific built-in exception that fits (`ArgumentOutOfRangeException`, `ArgumentNullException`, `InvalidOperationException`). This task chooses a fallback, which makes every input in the contract meaningful.

## Common misconception
Reading outside an array throws `IndexOutOfRangeException`, and a negative index throws it too, so check both ends: `index < 0` and `index >= values.Length`. `List<T>` throws `ArgumentOutOfRangeException` instead. Neither throwing behaviour satisfies this task. Catching every exception with `catch (Exception)` around a large block hides unrelated defects; catch only what you can handle.

## Worked example
```csharp
bool ok = int.TryParse("x", out int parsed);
bool ok2 = int.TryParse("12", out int parsed2);
```

ok is false and parsed is 0; ok2 is true and parsed2 is 12. This is one failure contract: a `bool` result plus an `out` value. The exercise below chooses a fallback value instead, so do not copy the TryParse shape into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000, passed as `long`. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```csharp
public static class Solution
{
    public static long SafeAt(long[] values, long index, long fallback)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Decide first whether the index is a valid position, covering both a negative index and one at or beyond the length, and return the fallback otherwise. Only then read the element. Trace the empty array, index -1 and an index equal to the length.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long SafeAt(long[] values, long index, long fallback)
    {
        if (index < 0 || index >= values.Length)
        {
            return fallback;
        }
        return values[index];
    }
}
```
