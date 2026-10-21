---
track: language
language: cpp
level: intermediate
order: 7
prerequisites: cpp-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: count_target
starter_code: "#include <string>\n#include <vector>\n\nlong long count_target(const std::vector<std::string>& words, const std::string& target) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# C++: Maps and frequency counting — Easy — Shared curriculum

## Learn
`std::unordered_map<K, V>` associates unique keys with values and offers average constant-time lookup. A frequency map counts how often each key appeared. `counts[key]` returns a reference to the value for `key`, first inserting a value-initialized element (0 for an integer) when the key is missing, which is why `++counts[word]` is the usual counting idiom. To ask whether a key exists without inserting it use `find` or `count`. Strings are compared by value with `==`.

Contract: `words` has 0 to 100 lowercase English words of length 1 to 20, `target` follows the same rule; return how often `target` occurs, as a `long long`.

## Common misconception
Reading with `counts[target]` is a write: if `target` never appeared, the map gains a new entry with value 0, and `operator[]` cannot be used on a `const` map at all. Use `find` (compare with `end()`) for a lookup that must not insert. `at(key)` does not insert either, but it throws `std::out_of_range` for a missing key. Do not assume every queried word has appeared.

## Worked example
```cpp
std::unordered_map<std::string, int> ages;
ages["Ada"] = 30;
bool known = ages.find("Ada") != ages.end();
```

known is true. "Ada" is the key and 30 is the associated value; `find` returns `end()` when the key is absent, and does not change the map.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```cpp
#include <string>
#include <vector>

long long count_target(const std::vector<std::string>& words, const std::string& target) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Count every word in an `unordered_map`, then look up the target without inserting it.

## Solutions
### C++
```cpp
#include <string>
#include <unordered_map>
#include <vector>

long long count_target(const std::vector<std::string>& words, const std::string& target) {
    std::unordered_map<std::string, long long> counts;
    for (const std::string& word : words) {
        ++counts[word];
    }
    auto it = counts.find(target);
    return it == counts.end() ? 0 : it->second;
}
```
