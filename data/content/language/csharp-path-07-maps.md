---
track: language
language: csharp
level: intermediate
order: 7
prerequisites: csharp-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_csharp: CountTarget
starter_code: "using System.Collections.Generic;\n\npublic static class Solution\n{\n    public static long CountTarget(string[] words, string target)\n    {\n        // Write your solution here.\n        return -1;\n    }\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# C#: Maps and frequency counting — Easy — Shared curriculum

## Learn
`Dictionary<TKey, TValue>` associates a key with a value, with expected O(1) lookup, insert and remove. A frequency map keeps how many times each key has appeared. The indexer `d[key]` throws `KeyNotFoundException` for a missing key, so use `TryGetValue(key, out value)` (which returns a `bool` and leaves `value` at its default when the key is absent) when absence is normal. `d[key] = v` adds or overwrites, while `Add` throws if the key already exists.

## Common misconception
`counts[word]++` on a word that has not been seen is not a harmless increment: reading the missing key throws `KeyNotFoundException`. Handle the missing case explicitly before incrementing. Do not rely on enumeration order: it often looks like insertion order, but code must not depend on it. Strings are compared by content, using ordinal comparison by default.

## Worked example
```csharp
var ages = new Dictionary<string, int>();
ages["Ada"] = 30;
bool known = ages.ContainsKey("Ada");
bool found = ages.TryGetValue("Bob", out int bobAge);
```

known is true; found is false and bobAge is 0. Ada is the key and 30 is the associated value.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static long CountTarget(string[] words, string target)
    {
        // Write your solution here.
        return -1;
    }
}
```

## Approach
Walk the words once, keeping a count per word, then look up the target. Make sure a word you have not seen yet starts from zero, and make sure a target that never appeared returns 0 instead of throwing.

## Solutions
### C#
```csharp
using System.Collections.Generic;

public static class Solution
{
    public static long CountTarget(string[] words, string target)
    {
        var counts = new Dictionary<string, long>();
        foreach (string word in words)
        {
            counts.TryGetValue(word, out long seen);
            counts[word] = seen + 1;
        }
        return counts.TryGetValue(target, out long total) ? total : 0;
    }
}
```
