---
track: language
language: cpp
level: intermediate
order: 10
prerequisites: cpp-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: safe_at
starter_code: "#include <vector>\n\nlong long safe_at(const std::vector<long long>& values, long long index, long long fallback) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# C++: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define the behaviour for invalid input explicitly: a fallback value, an `std::optional`, or an exception. This task chooses a fallback, making every input in the contract meaningful. `vector::operator[]` does not check its index: an out-of-range access is undefined behaviour, not an exception. `vector::at` does check and throws `std::out_of_range`.

Contract: `values` has length 0 to 100, `index` and `fallback` are `long long` values from -1000 to 1000; return `values[index]` when the index is valid and `fallback` otherwise. Never throw.

## Common misconception
`values[index]` with a bad index does not throw, so wrapping it in `try`/`catch` protects nothing; it is undefined behaviour. `values.at(index)` throws, which this task forbids. Validate negative indices as well as indices equal to or larger than the size. `size()` is unsigned, so convert deliberately: compare the signed index with 0 first, then cast. If you do catch, catch by const reference (`catch (const std::out_of_range& e)`); catching everything can hide unrelated defects.

## Worked example
```cpp
long long positive(long long value) {
    if (value <= 0) {
        throw std::invalid_argument("expected a positive value");
    }
    return value;
}

try {
    positive(0);
} catch (const std::invalid_argument& e) {
    // handled
}
```

Calling `positive(3)` returns 3; calling it with 0 throws. That is one failure contract. The exercise below deliberately chooses a fallback instead, so do not copy the exception behaviour into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not throw for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```cpp
#include <vector>

long long safe_at(const std::vector<long long>& values, long long index, long long fallback) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Reject a negative index or one at least as large as the size before touching the vector.

## Solutions
### C++
```cpp
#include <cstddef>
#include <vector>

long long safe_at(const std::vector<long long>& values, long long index, long long fallback) {
    if (index < 0 || index >= static_cast<long long>(values.size())) {
        return fallback;
    }
    return values[static_cast<std::size_t>(index)];
}
```
