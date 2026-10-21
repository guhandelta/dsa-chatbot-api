---
track: language
language: csharp
level: expert
order: 11
prerequisites: csharp-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: DigitSum
starter_code: "public static class Solution\n{\n    public static long DigitSum(long n)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# C#: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive method solves a smaller instance of the same contract. The base case supplies an answer without another call. A decreasing measure explains termination, and each call has its own parameters, locals and return point. Integer `/` truncates toward zero and `%` takes the sign of the dividend, so for a nonnegative `long`, `n / 10` drops the last digit and `n % 10` is that digit.

## Common misconception
Check that the recursive input strictly approaches the base case, and that the result of the recursive call contributes to the returned value. Recursion depth is limited by the thread's stack, and a `StackOverflowException` cannot be caught and ends the process; the available depth is not a fixed number, and very deep problems need an explicit stack. Fixed-width results still wrap: the factorial of 21 does not fit in a `long`.

## Worked example
```csharp
static long Factorial(long n)
{
    if (n <= 1)
    {
        return 1;
    }
    return n * Factorial(n - 1);
}
```

For n = 3 the calls are Factorial(3), Factorial(2), Factorial(1). The base case returns 1, which flows back through both callers to give 3 * 2 * 1 = 6. Factorial(20) is 2432902008176640000, but Factorial(21) wraps to a negative number in `long` arithmetic.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000, passed as `long`. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```csharp
public static class Solution
{
    public static long DigitSum(long n)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Split n into its last digit and the number that remains after dropping that digit, and let the same method handle the remainder. Decide which values of n need no further call. Trace n = 0, a single digit, and a number containing a zero digit such as 909.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long DigitSum(long n)
    {
        if (n < 10)
        {
            return n;
        }
        return n % 10 + DigitSum(n / 10);
    }
}
```
