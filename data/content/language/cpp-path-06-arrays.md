---
track: language
language: cpp
level: intermediate
order: 6
prerequisites: cpp-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: count_above
starter_code: "#include <vector>\n\nlong long count_above(const std::vector<long long>& values, long long threshold) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# C++: Arrays and lists — Easy — Shared curriculum

## Learn
`std::vector<T>` owns a contiguous, resizable sequence; `size()` is the number of elements and `capacity()` the room before it must reallocate. A vector has value semantics: assigning or passing one by value copies every element, so read-only parameters are normally `const std::vector<T>&`. A `const` reference also makes modification a compile error, which enforces the contract that `values` is not changed. Distinguish the index from the value at that index, and a copy from a reference to the same vector.

Contract: `values` has 0 to 1000 `long long` elements in -1000..1000; `threshold` is in the same range; return how many elements are strictly greater than `threshold`.

## Common misconception
Assigning one vector to another copies it, unlike Java or JavaScript arrays where assignment shares one array. Aliasing in C++ must be requested explicitly with a reference. Related traps: `for (auto v : values)` copies each element (cheap for `long long`, costly for strings), and `values[i]` is unchecked. Strictly greater excludes equal values.

## Worked example
```cpp
std::vector<int> scores{3, 8};
std::vector<int> copy = scores;
auto& alias = scores;
alias[0] = 5;
```

scores[0] is now 5 because alias is a reference to the same vector, while copy[0] is still 3 because `copy` was an independent copy made at initialization.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```cpp
#include <vector>

long long count_above(const std::vector<long long>& values, long long threshold) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Traverse the vector once with a range-based loop and count elements greater than the threshold.

## Solutions
### C++
```cpp
#include <vector>

long long count_above(const std::vector<long long>& values, long long threshold) {
    long long count = 0;
    for (long long value : values) {
        if (value > threshold) {
            ++count;
        }
    }
    return count;
}
```
