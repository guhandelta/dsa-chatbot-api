---
track: language
language: csharp
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: TotalCost
starter_code: "public static class Solution\n{\n    public static long TotalCost(long price, long quantity)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# C#: Values and arithmetic — Easy — Shared curriculum

## Learn
C# is statically typed: every variable has a type fixed at compile time. `int` is 32-bit and `long` is 64-bit; in this exercise the parameters and the result are `long`. Integer arithmetic on non-constant values wraps silently by default (an unchecked context) and throws `OverflowException` only in a checked context, so choose a type that can hold the result. A method returns its result to the caller rather than printing it.

## Common misconception
Widening the destination does not widen the arithmetic. With `int a = 100000, b = 100000;`, the statement `long wrong = a * b;` multiplies as `int` first, wraps to 1410065408, and only then converts to `long`; `(long)a * b` gives 10000000000. Cast an operand before the operation, not the result after it. A constant expression that overflows, such as `int.MaxValue + 1`, is a compile-time error instead (CS0220).

## Worked example
```csharp
int hours = 2;
int minutes = hours * 60;
long cents = 250L * 4;
```

minutes is 120 and cents is 1000. The suffix `L` makes the literal `250L` a `long`, so the multiplication happens in 64-bit arithmetic. Each variable is declared with a type that names what it holds.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000, passed as `long`; return the cost as `long`.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```csharp
public static class Solution
{
    public static long TotalCost(long price, long quantity)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Both parameters are already `long`, so one multiplication of the two values is enough and no cast is needed. Check the zero cases (price 0 or quantity 0) by trace before you submit.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long TotalCost(long price, long quantity)
    {
        return price * quantity;
    }
}
```
