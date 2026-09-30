---
track: algorithm
difficulty: Easy
algorithms: string
category: Data Structure
source: authored
io_mode: function
---
# String — Easy — Data Structure

A string is a sequence of characters stored as an array of code units, so indexing and scanning behave like an array. Strings are immutable in Python, JavaScript, TypeScript, Java, C#, Go and Rust's `&str`, so every modification creates a new string; collect pieces in a list or builder and join once, which is O(n) overall instead of O(n²). Taking a substring copies it in most languages, but is a zero-copy view in Go, Rust (`&s[a..b]`) and C++ (`std::string_view`). For lowercase letters, map a character to an index with `c - 'a'` (C, C++, Java, C#, Go), `ord(c) - ord('a')` (Python), `c.charCodeAt(0) - 97` (JavaScript, TypeScript), `c as u8 - b'a'` (Rust) or `c.ord - 97` (Ruby), then count in a 26-slot array.

| Problem family | Technique | Example problems |
| --- | --- | --- |
| Anagrams | 26-slot count array or sorted-string key; fixed-size sliding window for "all anagrams in s" | Valid anagram, group anagrams, find all anagrams in a string, permutation in string |
| Palindromes | Two pointers from both ends; expand around each of the 2n−1 centres in O(n²); Manacher in O(n) | Valid palindrome, longest palindromic substring, count palindromic substrings |
| Substring windows | Variable sliding window with a character-count map | Longest substring without repeating characters, minimum window substring |
| Subsequences | Two pointers, or DP over two strings | Is subsequence, longest common subsequence, edit distance |
| Parsing | Stack or index scanning | Decode string, basic calculator, valid parentheses |
| Pattern search | KMP, Z-algorithm, Rabin–Karp | Find the first occurrence, repeated substring pattern |

#### Anagram and palindrome checks — Python

```python
from collections import Counter

def is_anagram(s, t):
    return len(s) == len(t) and Counter(s) == Counter(t)

def find_anagrams(s, p):                    # start indices of p's anagrams in s
    need, window, res, k = Counter(p), Counter(), [], len(p)
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= k:
            left = s[i - k]
            window[left] -= 1
            if window[left] == 0:
                del window[left]
        if window == need:
            res.append(i - k + 1)
    return res

def is_palindrome(s):                       # letters and digits only, case-insensitive
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i += 1; j -= 1
    return True

def longest_palindrome(s):                  # expand around each centre, O(n²)
    best_lo, best_hi = 0, 0
    for c in range(len(s)):
        for lo, hi in ((c, c), (c, c + 1)):   # odd and even centres
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1; hi += 1
            if hi - lo - 1 > best_hi - best_lo:
                best_lo, best_hi = lo + 1, hi
    return s[best_lo:best_hi]
```
