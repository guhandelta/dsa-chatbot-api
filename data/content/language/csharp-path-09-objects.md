---
track: language
language: csharp
level: intermediate
order: 9
prerequisites: csharp-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: FinalBalance
starter_code: "public static class Solution\n{\n    public static long FinalBalance(long initial, long[] changes)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# C#: Objects, state, and references — Easy — Shared curriculum

## Learn
A `class` groups state in fields and is a reference type: assigning one class variable to another, or passing it to a method, copies the reference, so both names see the same object. A `struct` is a value type: assignment and passing copy the whole value. Updating a field changes that object; two separately created objects have separate state. Create the state inside the method so one call cannot affect another.

## Common misconception
`Counter c2 = c1;` for a class makes `c2` and `c1` the same object, so `c2.Value += 1` is visible through `c1`; for a `struct`, the same code changes only the copy. Mutating a struct stored in a `List<T>` does not compile: `list[i].Value = 5` is error CS1612 because the indexer returns a copy, although the same assignment on an array element works. Do not share a static account across calls.

## Worked example
```csharp
Counter first = new Counter();
Counter second = first;
second.Value += 1;

class Counter
{
    public int Value;
}
```

first.Value is 1. Both variables refer to one object. If Counter were declared as a `struct`, first.Value would stay 0 because `second` would be a copy.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000, passed as `long` (changes as `long[]`); changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```csharp
public static class Solution
{
    public static long FinalBalance(long initial, long[] changes)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Create a fresh account object whose balance starts at initial, apply each change in order, and return the balance. Keep the account local to the call. Trace an empty changes array and a balance that goes negative.

## Solutions
### C#
```csharp
public static class Solution
{
    public static long FinalBalance(long initial, long[] changes)
    {
        var account = new Account { Balance = initial };
        foreach (long change in changes)
        {
            account.Balance += change;
        }
        return account.Balance;
    }

    private sealed class Account
    {
        public long Balance;
    }
}
```
