---
track: language
language: csharp
level: beginner
order: 3
prerequisites: csharp-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: SumThrough
starter_code: "public static class Solution\n{\n    public static long SumThrough(long n)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# C#: Loops and accumulation — Easy — Shared curriculum

## Learn
A `for` loop has an initializer, a condition checked before every iteration, and an update. `foreach` visits each element of a collection. An accumulator stores the result of everything visited so far; say what it means before and after each iteration. Pick its type for the final value: an `int` accumulator wraps silently once the total exceeds 2147483647, because non-constant arithmetic is unchecked by default.

## Common misconception
An off-by-one error changes which values are visited: `i < n` stops one short of `i <= n`. Check n = 0 and n = 1 by tracing the initializer, the condition, the update and the return. The accumulator must be declared outside the loop so it survives each iteration. Summing 1 through 100000 in an `int` prints 705082704, while a `long` accumulator gives the correct 5000050000.

## Worked example
```csharp
long product = 1;
for (int i = 1; i <= 3; i++)
{
    product *= i;
}
```

product goes from 1 to 1, then 2, then 6. Before each iteration it is the product of the integers visited so far; starting it at 0 would make every result 0.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000, passed as `long`. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```csharp
public static class Solution
{
    public static long SumThrough(long n)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Start an accumulator at zero, visit each integer from 1 through n once, add it, and return the accumulator after the loop. Trace n = 0 (the loop body never runs) and n = 1.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long SumThrough(long n)
    {
        long total = 0;
        for (long i = 1; i <= n; i++)
        {
            total += i;
        }
        return total;
    }
}
```
