---
track: language
language: c
level: beginner
order: 5
prerequisites: c-path-04-functions
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: count_vowels
starter_code: "long long count_vowels(const char* text) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [""], "expected": 0}, {"args": ["a"], "expected": 1}, {"args": ["rhythm"], "expected": 0}, {"args": ["hello"], "expected": 2}, {"args": ["aeiou"], "expected": 5}, {"args": ["banana"], "expected": 3}]
---
# C: Strings and iteration — Easy — Shared curriculum

## Learn
A C string is an array of `char` that ends with a zero byte, `'\0'`. The length is the number of characters before that terminator, so storing n characters needs n + 1 bytes. Indices start at 0 and the last valid index is `length - 1`. `strlen` finds the length by walking to the terminator, which costs O(n); compute it once rather than in a loop condition, or walk the string until you reach `'\0'`. A parameter that only reads the text should be `const char*`. Single quotes make a character constant (`'a'`), double quotes make a string (`"a"` is two bytes: `a` and the terminator).

The contract here: `text` is a valid terminated string of 0 to 1000 lowercase English letters (the exercise deliberately restricts the alphabet), and the function returns the number of vowels `a`, `e`, `i`, `o`, `u` as a `long long`.

## Common misconception
A string's length is not `sizeof`. Inside a function the parameter `const char* text` is a pointer, so `sizeof(text)` is the size of the pointer (8 on a typical 64-bit platform) whatever the string contains; even on a real array, `sizeof` also counts the terminator. Use `strlen` or stop at `'\0'`. Also remember that the valid indices stop at `length - 1`: reading `text[length]` returns the terminator, and reading beyond it is undefined behaviour.

## Worked example
```c
char word[] = "cat";
size_t length = strlen(word);
char first = word[0];
char last = word[length - 1];
```

`length` is 3, `first` is `'c'` and `last` is `'t'`; the valid indices are 0, 1 and 2. `sizeof word` is 4 because the array also holds the terminator, which `strlen` does not count. Calling `strlen` needs `#include <string.h>`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count the lowercase English vowels a, e, i, o, u in text. text contains only lowercase English letters and has length 0 to 1000. Return the count.

## Example
Arguments: `[""]` → `0`

## Starter code
```c
long long count_vowels(const char* text) {
    // Write your solution here.
    return 0;
}
```

## Approach
Visit each character once, from the first until the terminator, and test whether it is one of the five vowels (a comparison chain, a `switch`, or a lookup in the string `"aeiou"` all work). Add one to a counter that starts at 0 for each match; the empty string never enters the loop.

## Solutions
### C
```c
#include <string.h>

long long count_vowels(const char* text) {
    long long count = 0;
    for (size_t i = 0; text[i] != '\0'; i++) {
        if (strchr("aeiou", text[i]) != NULL) {
            count++;
        }
    }
    return count;
}
```
