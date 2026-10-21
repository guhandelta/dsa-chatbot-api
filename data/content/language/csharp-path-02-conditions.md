---
track: language
language: csharp
level: beginner
order: 2
prerequisites: csharp-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: InRange
starter_code: "public static class Solution\n{\n    public static bool InRange(long value, long low, long high)\n    {\n        // Write your solution here.\n        return false;\n    }\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# C#: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition has type `bool`. Combine conditions with `&&` when both must hold or `||` when either suffices; both operators short-circuit, so the right operand is evaluated only when the left one does not already decide the result. Boundary words such as inclusive decide whether a comparison uses `<` or `<=`. Relational patterns such as `age is >= 16 and <= 25` read well when the bounds are constants.

## Common misconception
A chained mathematical comparison does not translate into C#. `1 <= x <= 5` does not compile: `1 <= x` produces a `bool`, and `<=` cannot then compare that `bool` with `5` (CS0019). Write both comparisons explicitly. A relational pattern also needs a constant on its right-hand side: `x is >= low` is error CS9135 when `low` is a variable.

## Worked example
```csharp
int age = 18;
bool canJoin = age is >= 16 and <= 25;
bool sameRule = age >= 16 && age <= 25;
```

Both variables are true. The pattern form uses constant bounds; the `&&` form works with any values. Test each boundary independently when you translate a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000, passed as `long`.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```csharp
public static class Solution
{
    public static bool InRange(long value, long low, long high)
    {
        // Write your solution here.
        return false;
    }
}
```

## Approach
State the rule as two comparisons that must both hold and decide for each whether the boundary is included. Trace value equal to low, value equal to high, and one value just outside each end.

## Solutions
### C#
```csharp
public static class Solution
{
    public static bool InRange(long value, long low, long high)
    {
        return value >= low && value <= high;
    }
}
```
