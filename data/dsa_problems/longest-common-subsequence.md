---
track: dsa
difficulty: Medium
source: leetcode
io_mode: function
algorithms: dynamic-programming
fn_python: longest_common_subsequence
fn_javascript: longestCommonSubsequence
test_cases: [{"args": ["abcde", "ace"], "expected": 3}, {"args": ["abc", "abc"], "expected": 3}, {"args": ["abc", "def"], "expected": 0}, {"args": ["", "abc"], "expected": 0}, {"args": ["a", "a"], "expected": 1}, {"args": ["bsbininm", "jmjkbkjkv"], "expected": 1}]
---
# Longest Common Subsequence (LC 1143) — Medium — DP (2D)

## Problem
Given two strings, return the length of their longest common subsequence (characters in order, not necessarily contiguous); 0 if none.

## Example
"abcde", "ace" → 3

## Approach
2D DP: dp[i][j] = LCS of prefixes text1[..i], text2[..j]. Matching chars extend the diagonal; otherwise take the best of dropping one char. Time O(mn), space O(mn) (reducible to two rows).

## Hints
- If text1[i-1] == text2[j-1]: dp[i][j] = dp[i-1][j-1] + 1.
- Else dp[i][j] = max(dp[i-1][j], dp[i][j-1]).

## Solutions
*Conventions: C++ assumes `<bits/stdc++.h>` + `using namespace std;`. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution` on LeetCode.*

### Python
```python
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

### JavaScript
```javascript
function longestCommonSubsequence(text1, text2) {
  const m = text1.length, n = text2.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = text1[i - 1] === text2[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1]);
  return dp[m][n];
}
```

### Java
```java
public int longestCommonSubsequence(String text1, String text2) {
    int m = text1.length(), n = text2.length();
    int[][] dp = new int[m + 1][n + 1];
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = text1.charAt(i - 1) == text2.charAt(j - 1)
                ? dp[i - 1][j - 1] + 1
                : Math.max(dp[i - 1][j], dp[i][j - 1]);
    return dp[m][n];
}
```

### C++
```cpp
int longestCommonSubsequence(string text1, string text2) {
    int m = text1.size(), n = text2.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = text1[i - 1] == text2[j - 1]
                ? dp[i - 1][j - 1] + 1
                : max(dp[i - 1][j], dp[i][j - 1]);
    return dp[m][n];
}
```

### C
```c
int longestCommonSubsequence(char* text1, char* text2) {
    int m = strlen(text1), n = strlen(text2);
    int* prev = calloc(n + 1, sizeof(int));
    int* cur = calloc(n + 1, sizeof(int));
    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (text1[i - 1] == text2[j - 1]) cur[j] = prev[j - 1] + 1;
            else cur[j] = prev[j] > cur[j - 1] ? prev[j] : cur[j - 1];
        }
        int* t = prev; prev = cur; cur = t;
        memset(cur, 0, (n + 1) * sizeof(int));
    }
    int res = prev[n];
    free(prev); free(cur);
    return res;
}
```

### Rust
```rust
pub fn longest_common_subsequence(text1: String, text2: String) -> i32 {
    let (a, b) = (text1.as_bytes(), text2.as_bytes());
    let (m, n) = (a.len(), b.len());
    let mut dp = vec![vec![0i32; n + 1]; m + 1];
    for i in 1..=m {
        for j in 1..=n {
            dp[i][j] = if a[i - 1] == b[j - 1] {
                dp[i - 1][j - 1] + 1
            } else {
                dp[i - 1][j].max(dp[i][j - 1])
            };
        }
    }
    dp[m][n]
}
```
