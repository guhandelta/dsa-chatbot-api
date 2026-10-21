---
track: language
language: csharp
level: intermediate
order: 8
prerequisites: csharp-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: UniqueCount
starter_code: "using System.Collections.Generic;\n\npublic static class Solution\n{\n    public static long UniqueCount(long[] values)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# C#: Sets and equality — Easy — Shared curriculum

## Learn
`HashSet<T>` records membership and stores each distinct element once, with expected O(1) add, contains and remove. `Add` returns `false` when the element was already present, and adding a duplicate does not increase `Count`. Choose a set when you need uniqueness and a dictionary when each key also needs a value. Which elements count as equal is decided by `Equals` and `GetHashCode`.

## Common misconception
Do not depend on enumeration order from a hash set. Equality follows the element type: two strings with the same content are one element, and tuples such as `(int, int)` compare structurally, but two different `int[]` arrays with the same contents are two elements because arrays compare by reference. For primitive `long` values, equal numbers are always one element.

## Worked example
```csharp
var visited = new HashSet<int>();
bool first = visited.Add(7);
bool second = visited.Add(7);
bool found = visited.Contains(7);
```

first is true, second is false, found is true, and visited.Count is 1. Adding the same number twice does not create two entries.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000, passed as `long[]`.

## Example
Arguments: `[[]]` → `0`

## Starter code
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static long UniqueCount(long[] values)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Put every element into a set and report how many entries the set holds; the set removes duplicates for you. Trace the empty array, an array whose elements are all equal, and an array holding both 3 and -3 (two different values, so two entries).

## Solutions
### C#
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static long UniqueCount(long[] values)
    {
        var seen = new HashSet<long>(values);
        return seen.Count;
    }
}
```
