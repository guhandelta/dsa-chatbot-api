---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: dynamic-programming, strings
fn_python: word_break
fn_javascript: wordBreak
test_cases: [{"args": ["leetcode", ["leet", "code"]], "expected": true}, {"args": ["applepenapple", ["apple", "pen"]], "expected": true}, {"args": ["catsandog", ["cats", "dog", "sand", "and", "cat"]], "expected": false}, {"args": ["a", ["a"]], "expected": true}, {"args": ["ab", ["a"]], "expected": false}, {"args": ["cars", ["car", "ca", "rs"]], "expected": true}]
---
# Word Break (LC 139) — Medium — DP, Strings

## Problem
Return true if string `s` can be segmented into a sequence of one or more words from `wordDict` (words reusable).

## Example
s = "leetcode", wordDict = ["leet","code"] → true

## Approach
dp[i] = can s[0..i) be segmented. dp[0]=true; dp[i] is true if some j < i has dp[j] and s[j..i) in the dictionary (use a set). Time O(n^2 · L) worst case, space O(n).

## Hints
- Think "is every prefix breakable?"
- Bound the inner loop by the max word length for speed.

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def word_break(s, word_dict):
    words = set(word_dict)
    max_len = max(map(len, words)) if words else 0
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - max_len), i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[len(s)]
```

### JavaScript
```javascript
function wordBreak(s, wordDict) {
  const words = new Set(wordDict);
  const maxLen = Math.max(...wordDict.map(w => w.length));
  const dp = new Array(s.length + 1).fill(false);
  dp[0] = true;
  for (let i = 1; i <= s.length; i++)
    for (let j = Math.max(0, i - maxLen); j < i; j++)
      if (dp[j] && words.has(s.slice(j, i))) { dp[i] = true; break; }
  return dp[s.length];
}
```

### Java
```java
public boolean wordBreak(String s, List<String> wordDict) {
    Set<String> words = new HashSet<>(wordDict);
    int maxLen = 0;
    for (String w : wordDict) maxLen = Math.max(maxLen, w.length());
    boolean[] dp = new boolean[s.length() + 1];
    dp[0] = true;
    for (int i = 1; i <= s.length(); i++)
        for (int j = Math.max(0, i - maxLen); j < i; j++)
            if (dp[j] && words.contains(s.substring(j, i))) { dp[i] = true; break; }
    return dp[s.length()];
}
```

### C++
```cpp
bool wordBreak(string s, vector<string>& wordDict) {
    unordered_set<string> words(wordDict.begin(), wordDict.end());
    size_t maxLen = 0;
    for (auto& w : wordDict) maxLen = max(maxLen, w.size());
    vector<bool> dp(s.size() + 1, false);
    dp[0] = true;
    for (size_t i = 1; i <= s.size(); i++)
        for (size_t j = i > maxLen ? i - maxLen : 0; j < i; j++)
            if (dp[j] && words.count(s.substr(j, i - j))) { dp[i] = true; break; }
    return dp[s.size()];
}
```

### C
```c
bool wordBreak(char* s, char** wordDict, int wordDictSize) {
    int n = strlen(s);
    bool* dp = calloc(n + 1, sizeof(bool));
    dp[0] = true;
    for (int i = 1; i <= n; i++) {
        for (int w = 0; w < wordDictSize && !dp[i]; w++) {
            int len = strlen(wordDict[w]);
            if (len <= i && dp[i - len] && strncmp(s + i - len, wordDict[w], len) == 0)
                dp[i] = true;
        }
    }
    bool res = dp[n];
    free(dp);
    return res;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn word_break(s: String, word_dict: Vec<String>) -> bool {
    let words: HashSet<&str> = word_dict.iter().map(|w| w.as_str()).collect();
    let max_len = word_dict.iter().map(|w| w.len()).max().unwrap_or(0);
    let n = s.len();
    let mut dp = vec![false; n + 1];
    dp[0] = true;
    for i in 1..=n {
        let start = i.saturating_sub(max_len);
        for j in start..i {
            if dp[j] && words.contains(&s[j..i]) {
                dp[i] = true;
                break;
            }
        }
    }
    dp[n]
}
```
