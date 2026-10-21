---
track: language
language: cpp
level: intermediate
order: 8
prerequisites: cpp-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: unique_count
starter_code: "#include <vector>\n\nlong long unique_count(const std::vector<long long>& values) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# C++: Sets and equality — Easy — Shared curriculum

## Learn
A set records membership and stores each distinct key once. `std::unordered_set<T>` uses hashing (average constant time) and `insert` returns a pair whose `second` is `false` when the key was already there; `size()` is the number of distinct keys. The ordered `std::set<T>` keeps keys sorted by a comparator, and two keys count as the same when neither compares less than the other. Choose a set when you need uniqueness and a map when each key also needs a value.

Contract: `values` has 0 to 1000 `long long` elements in -1000..1000; return the number of distinct values as a `long long`.

## Common misconception
Do not depend on the iteration order of an `unordered_set`; it is unspecified. In an ordered `std::set` equality comes from the comparator, not from `==`: a comparator that looks at only one field silently merges distinct elements that tie on it. For plain integers both behave as expected, but remember that equality means the identical value: 1 and -1 are different keys, and equal values that appear far apart in the input are still one key. Note also that `size()` is a `std::size_t`, so convert explicitly when the contract returns `long long`.

## Worked example
```cpp
std::unordered_set<int> visited;
visited.insert(7);
bool added_again = visited.insert(7).second;
bool found = visited.count(7) == 1;
```

added_again is false, found is true, and `visited.size()` is 1. Adding the same key twice does not create two entries.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```cpp
#include <vector>

long long unique_count(const std::vector<long long>& values) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Put every element into a hash set and report how many distinct keys it holds.

## Solutions
### C++
```cpp
#include <unordered_set>
#include <vector>

long long unique_count(const std::vector<long long>& values) {
    std::unordered_set<long long> seen(values.begin(), values.end());
    return static_cast<long long>(seen.size());
}
```
