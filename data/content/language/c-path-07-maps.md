---
track: language
language: c
level: intermediate
order: 7
prerequisites: c-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: count_target
starter_code: "#include <stddef.h>\n\nlong long count_target(char** words, size_t n, const char* target) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# C: Maps and frequency counting — Easy — Shared curriculum

## Learn
A map associates a key with a value, and a frequency map keeps a count per key. C's standard library has no map type: you build one from parallel arrays, a hash table or a tree (or use POSIX `hsearch`). Whatever you build, keys that are strings must be compared by content with `strcmp`, which returns 0 when the texts are equal; `==` on two `char*` compares addresses. A lookup for a key that was never inserted needs an explicit "not found" result before you increment or report a count.

The contract here: `words` is an array of `n` valid strings (`n` is 0 to 100, each word has 1 to 20 lowercase letters), `target` follows the same rule, and the function returns how many entries equal `target` exactly, so `"aa"` does not count for `"a"`. Strings are passed as `char*` and an array of strings as `char**` plus its length; the elements must not be modified.

## Common misconception
`words[i] == target` asks whether the two pointers hold the same address, not whether the texts match. It can look as if it works, because a compiler may merge identical string literals into one array, and then fail as soon as the text comes from a buffer, a file or user input. Compare contents with `strcmp(a, b) == 0`. Also do not dereference entries of an empty array: when `n` is 0 there is nothing to read.

## Worked example
```c
const char* names[] = {"Ada", "Alan"};
long long ages[] = {30, 41};
long long age = -1;
for (size_t i = 0; i < 2; i++) {
    if (strcmp(names[i], "Alan") == 0) {
        age = ages[i];
    }
}
```

Index `i` links a key in `names` to its value in `ages`, so `age` becomes 41; if no name matched, `age` would stay at the "not found" value -1. This map uses parallel arrays and a linear search. The key is compared with `strcmp`, not `==`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. A frequency map is the general technique (in C you build it yourself or compare keys directly with strcmp). words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0` (the C call is `count_target(words, 0, "a")`)

## Starter code
```c
#include <stddef.h>

long long count_target(char** words, size_t n, const char* target) {
    // Write your solution here.
    return 0;
}
```

## Approach
Counting a single target is a frequency map with one counter: look at every word, compare it with `target` by content, and increment the counter on equality. Remember that a longer word that merely begins with the target is a different key.

## Solutions
### C
```c
#include <stddef.h>
#include <string.h>

long long count_target(char** words, size_t n, const char* target) {
    long long count = 0;
    for (size_t i = 0; i < n; i++) {
        if (strcmp(words[i], target) == 0) {
            count++;
        }
    }
    return count;
}
```
