---
track: algorithm
difficulty: Medium
algorithms: string-matching
category: Algorithm
source: authored
io_mode: function
---
# String pattern matching — Medium — Algorithm

Naive matching tries every alignment in O(nk) for text length n and pattern length k. Linear-time algorithms avoid re-reading text characters.

| Algorithm | Time | Idea | Use when |
| --- | --- | --- | --- |
| KMP | O(n + k) | Failure function: longest proper prefix of the pattern that is also a suffix at each position | Single pattern, guaranteed linear time |
| Z-algorithm | O(n + k) | Z\[i\] = length of the longest prefix match starting at i; run on `pattern + "$" + text` | Single pattern, prefix-based problems |
| Rabin–Karp | O(n + k) average | Rolling polynomial hash, verify on a hash match | Many patterns of one length, duplicate substrings |
| Aho–Corasick | O(n + total pattern length + matches) | Trie of patterns with failure links | Many patterns at once |
| Manacher | O(n) | Reuses mirror palindrome radii | Longest palindromic substring |
| Suffix array + LCP | O(n log n) build | Sorted suffixes with longest common prefixes | Distinct substrings, longest repeated substring |

Built-in substring search (fine for most problems): Python `str.find`, JavaScript and TypeScript `indexOf`, Java `indexOf`, C# `IndexOf(s, StringComparison.Ordinal)`, C `strstr`, C++ `std::string::find` or `std::boyer_moore_searcher`, Go `strings.Index`, Rust `str::find`, Ruby `String#index`.

#### KMP search — Python

```python
def kmp_search(text, pat):
    fail, k = [0] * len(pat), 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]:
            k = fail[k - 1]
        if pat[i] == pat[k]:
            k += 1
        fail[i] = k
    matches, k = [], 0
    for i, ch in enumerate(text):
        while k and ch != pat[k]:
            k = fail[k - 1]
        if ch == pat[k]:
            k += 1
        if k == len(pat):
            matches.append(i - k + 1)
            k = fail[k - 1]
    return matches
```

#### Rabin–Karp search — Python

```python
def rabin_karp(text, pat, base=131, mod=(1 << 61) - 1):
    n, k = len(text), len(pat)
    if k > n:
        return []
    hp = ht = 0
    power = pow(base, k - 1, mod)
    for i in range(k):
        hp = (hp * base + ord(pat[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    matches = []
    for i in range(n - k + 1):
        if hp == ht and text[i:i + k] == pat:
            matches.append(i)
        if i + k < n:
            ht = ((ht - ord(text[i]) * power) * base + ord(text[i + k])) % mod
    return matches
```
