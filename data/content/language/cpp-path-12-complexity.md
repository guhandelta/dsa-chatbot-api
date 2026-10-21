---
track: language
language: cpp
level: expert
order: 12
prerequisites: cpp-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: has_pair
starter_code: "#include <vector>\n\nbool has_pair(const std::vector<long long>& values, long long target) {\n    // Write your solution here.\n    return false;\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# C++: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. A single traversal that does one `unordered_set` operation per element does expected O(n) work: hash operations are O(1) on average but O(n) in the worst case, and the average assumes a good hash. Count how often operations run, including copies and hashing, not just lines of code. An invariant states what is true before each iteration; here, before visiting index i the set holds exactly the values at indices below i.

Contract: `values` has length 0 to 1000 with elements and `target` in -1000..1000; return `true` when two elements at different indices sum to `target`, as a `bool`.

## Common misconception
Two different indices may hold the same value, but one index must never pair with itself: look up the complement before inserting the current value, or `[1]` with target 2 would wrongly succeed. The two indices need not be neighbours or involve the first element, and values and target may be negative or zero; check those cases yourself because six tests cannot cover every shape. A correct result on six tests is evidence, not a proof; explain your invariant and complexity as part of the mastery check.

## Worked example
```cpp
std::vector<int> values{4, 7, 9};
int single = 0;
int nested = 0;
for (std::size_t i = 0; i < values.size(); ++i) {
    ++single;
    for (std::size_t j = 0; j < values.size(); ++j) {
        ++nested;
    }
}
```

single is 3 and nested is 9: n visits for n elements, and n × n visits when a complete second traversal sits inside each visit. Always count how often operations run, not just how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```cpp
#include <vector>

bool has_pair(const std::vector<long long>& values, long long target) {
    // Write your solution here.
    return false;
}
```

## Approach
Use the language construct in this lesson. Scan once; for each element ask whether its complement was already seen, then remember the element.

## Solutions
### C++
```cpp
#include <unordered_set>
#include <vector>

bool has_pair(const std::vector<long long>& values, long long target) {
    std::unordered_set<long long> seen;
    for (long long value : values) {
        if (seen.count(target - value) == 1) {
            return true;
        }
        seen.insert(value);
    }
    return false;
}
```
