---
track: language
language: cpp
level: beginner
order: 5
prerequisites: cpp-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: count_vowels
starter_code: "#include <string>\n\nlong long count_vowels(const std::string& text) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# C++: Strings and iteration — Easy — Shared curriculum

## Learn
`std::string` owns a mutable sequence of bytes stored contiguously. `text[i]` is a `char`; valid indices are 0 through `size() - 1`, and `operator[]` does not check them. `size()` returns an unsigned `std::size_t`. A range-based `for (char ch : text)` visits each byte once without an index. Take a read-only string as `const std::string&` so it is not copied. The definition of character matters: this exercise restricts inputs to lowercase English letters, where one byte is one letter.

Contract: `text` holds only lowercase English letters, length 0 to 1000; return the number of the letters a, e, i, o, u as a `long long`.

## Common misconception
Do not read index `size()`: the last valid index is `size() - 1`. Because `size()` is unsigned, `size() - 1` on an empty string does not give -1; it wraps to the largest `std::size_t`, so a loop condition such as `i <= text.size() - 1` is always true for an empty string and runs far past the end. Compare against `size()` directly (`i < text.size()`). Single quotes make a `char` (`'a'`), double quotes a string literal (`"a"`), and they are not interchangeable.

## Worked example
```cpp
std::string word = "cat";
char first = word[0];
std::size_t length = word.size();
if (!word.empty()) {
    char last = word.back();
}
```

first is `'c'`, length is 3 and last is `'t'`. Valid indices are 0, 1 and 2, and `back()` on an empty string would be undefined, so the example checks `empty()` first.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```cpp
#include <string>

long long count_vowels(const std::string& text) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Visit every character once and count those that are one of the five vowel letters.

## Solutions
### C++
```cpp
#include <string>

long long count_vowels(const std::string& text) {
    long long count = 0;
    for (char ch : text) {
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') {
            ++count;
        }
    }
    return count;
}
```
