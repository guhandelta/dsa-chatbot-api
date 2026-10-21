---
track: language
language: csharp
level: beginner
order: 4
prerequisites: csharp-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: Distance
starter_code: "public static class Solution\n{\n    public static long Distance(long a, long b)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# C#: Functions and contracts — Easy — Shared curriculum

## Learn
A method contract names its parameters, its return type and the valid inputs. Parameters are local variables initialised from the arguments, and all of them are passed by value unless marked `ref`, `out` or `in`. A `return` ends the call; printing does not satisfy a return-value contract. Expression-bodied members such as `static long Double(long v) => v * 2;` are shorthand for a single `return`.

## Common misconception
Keep the method name, parameter order and types unchanged because the caller depends on them. Assigning to a parameter changes only the method's own copy: after `static void Bump(int x) { x = x + 1; }`, calling `Bump(n)` leaves `n` unchanged, and only `ref` passes the caller's variable itself. Negative positions still have a nonnegative distance. `Math.Abs` throws `OverflowException` for the minimum value of its type (`int.MinValue`, `long.MinValue`), a boundary outside this exercise's inputs.

## Worked example
```csharp
static long Double(long value)
{
    return value * 2;
}
long result = Double(4);
```

The argument 4 becomes the parameter value for this call and result is 8. A second call gets its own parameter variable. The exercise runner calls your static method directly; you do not need a `Main`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied method signature and return a `long`.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```csharp
public static class Solution
{
    public static long Distance(long a, long b)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Distance is the size of the difference, regardless of which argument is larger. Use a framework method for absolute value or compare the arguments first, then trace [5, 2], [0, 0] and a pair with different signs.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long Distance(long a, long b)
    {
        return Math.Abs(a - b);
    }
}
```
