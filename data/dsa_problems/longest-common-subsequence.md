---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: dynamic-programming
fn_python: longest_common_subsequence
fn_javascript: longestCommonSubsequence
fn_typescript: longestCommonSubsequence
fn_java: longestCommonSubsequence
fn_cpp: longestCommonSubsequence
fn_c: longestCommonSubsequence
fn_rust: longest_common_subsequence
fn_go: longestCommonSubsequence
fn_csharp: LongestCommonSubsequence
fn_ruby: longest_common_subsequence
test_cases: [{"args": ["cab", "bca"], "expected": 2}, {"args": ["", ""], "expected": 0}, {"args": ["xyz", "xyz"], "expected": 3}, {"args": ["aaaa", "aa"], "expected": 2}, {"args": ["mississippi", "msp"], "expected": 3}, {"args": ["abcdefg", "gfedcba"], "expected": 1}, {"args": ["planet", "pnt"], "expected": 3}, {"args": ["ab", "ba"], "expected": 1}, {"args": ["abcabcabc", "cbacbacba"], "expected": 5}, {"args": ["", "abc"], "expected": 0}]
---
# Longest Shared Subsequence — Medium — DP (2D)

## Problem
You are given two strings `text1` and `text2` made of lowercase letters. Either string may be empty.

A subsequence of a string is obtained by deleting zero or more of its characters, keeping the rest in their original order. Return the length of the longest string that is a subsequence of both `text1` and `text2`. If the two strings share no character, return 0.

## Example
text1 = "elbow", text2 = "below" → 4 (for example "elow")

## Approach
Let `table[i][j]` be the answer for the first `i` characters of `text1` and the first `j` characters of `text2`. If the characters at positions `i` and `j` are equal, the best match extends `table[i-1][j-1]` by one. Otherwise, the best answer drops the last character of one string or the other, so take the larger of `table[i-1][j]` and `table[i][j-1]`. Time O(mn), space O(mn).

## Hints
- In each cell, only the last character of each prefix needs to be compared.
- If you only need the length, two rows of the table are enough.

## Solutions
*Conventions: C++ code uses `std::` names and includes the headers it needs. Java code sits in `class Solution` with `import java.util.*;`. Rust functions go inside `impl Solution`.*

### Python
```python
def longest_common_subsequence(text1, text2):
    rows, cols = len(text1) + 1, len(text2) + 1
    table = [[0] * cols for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            if text1[i - 1] == text2[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[-1][-1]
```

### JavaScript
```javascript
function longestCommonSubsequence(text1, text2) {
  const rows = text1.length + 1, cols = text2.length + 1;
  const table = Array.from({ length: rows }, () => new Array(cols).fill(0));
  for (let i = 1; i < rows; i++)
    for (let j = 1; j < cols; j++)
      table[i][j] = text1[i - 1] === text2[j - 1]
        ? table[i - 1][j - 1] + 1
        : Math.max(table[i - 1][j], table[i][j - 1]);
  return table[rows - 1][cols - 1];
}
```

### TypeScript
```typescript
function longestCommonSubsequence(text1: string, text2: string): number {
  const rows = text1.length + 1, cols = text2.length + 1;
  const table: number[][] = Array.from({ length: rows }, () => new Array(cols).fill(0));
  for (let i = 1; i < rows; i++)
    for (let j = 1; j < cols; j++)
      table[i][j] = text1[i - 1] === text2[j - 1]
        ? table[i - 1][j - 1] + 1
        : Math.max(table[i - 1][j], table[i][j - 1]);
  return table[rows - 1][cols - 1];
}
```

### Java
```java
public int longestCommonSubsequence(String text1, String text2) {
    int rows = text1.length() + 1, cols = text2.length() + 1;
    int[][] table = new int[rows][cols];
    for (int i = 1; i < rows; i++)
        for (int j = 1; j < cols; j++)
            table[i][j] = text1.charAt(i - 1) == text2.charAt(j - 1)
                ? table[i - 1][j - 1] + 1
                : Math.max(table[i - 1][j], table[i][j - 1]);
    return table[rows - 1][cols - 1];
}
```

### C++
```cpp
int longestCommonSubsequence(std::string text1, std::string text2) {
    int rows = (int)text1.size() + 1, cols = (int)text2.size() + 1;
    std::vector<std::vector<int>> table(rows, std::vector<int>(cols, 0));
    for (int i = 1; i < rows; i++)
        for (int j = 1; j < cols; j++)
            table[i][j] = text1[i - 1] == text2[j - 1]
                ? table[i - 1][j - 1] + 1
                : std::max(table[i - 1][j], table[i][j - 1]);
    return table[rows - 1][cols - 1];
}
```

### C
```c
long long longestCommonSubsequence(char* text1, char* text2) {
    int m = strlen(text1), n = strlen(text2);
    int* above = calloc(n + 1, sizeof(int));
    int* below = calloc(n + 1, sizeof(int));
    for (int i = 1; i <= m; i++) {
        below[0] = 0;
        for (int j = 1; j <= n; j++) {
            if (text1[i - 1] == text2[j - 1]) below[j] = above[j - 1] + 1;
            else below[j] = above[j] > below[j - 1] ? above[j] : below[j - 1];
        }
        int* tmp = above;
        above = below;
        below = tmp;
    }
    long long result = above[n];
    free(above);
    free(below);
    return result;
}
```

### Rust
```rust
pub fn longest_common_subsequence(text1: String, text2: String) -> i32 {
    let a = text1.as_bytes();
    let b = text2.as_bytes();
    let mut table = vec![vec![0i32; b.len() + 1]; a.len() + 1];
    for i in 1..=a.len() {
        for j in 1..=b.len() {
            table[i][j] = if a[i - 1] == b[j - 1] {
                table[i - 1][j - 1] + 1
            } else {
                table[i - 1][j].max(table[i][j - 1])
            };
        }
    }
    table[a.len()][b.len()]
}
```

### Go
```go
func longestCommonSubsequence(text1 string, text2 string) int {
	rows, cols := len(text1)+1, len(text2)+1
	table := make([][]int, rows)
	for i := range table {
		table[i] = make([]int, cols)
	}
	for i := 1; i < rows; i++ {
		for j := 1; j < cols; j++ {
			if text1[i-1] == text2[j-1] {
				table[i][j] = table[i-1][j-1] + 1
			} else if table[i-1][j] >= table[i][j-1] {
				table[i][j] = table[i-1][j]
			} else {
				table[i][j] = table[i][j-1]
			}
		}
	}
	return table[rows-1][cols-1]
}
```

### C#
```csharp
public static int LongestCommonSubsequence(string text1, string text2) {
    int rows = text1.Length + 1, cols = text2.Length + 1;
    int[,] table = new int[rows, cols];
    for (int i = 1; i < rows; i++)
        for (int j = 1; j < cols; j++)
            table[i, j] = text1[i - 1] == text2[j - 1]
                ? table[i - 1, j - 1] + 1
                : Math.Max(table[i - 1, j], table[i, j - 1]);
    return table[rows - 1, cols - 1];
}
```

### Ruby
```ruby
def longest_common_subsequence(text1, text2)
  rows = text1.length + 1
  cols = text2.length + 1
  table = Array.new(rows) { Array.new(cols, 0) }
  (1...rows).each do |i|
    (1...cols).each do |j|
      table[i][j] = if text1[i - 1] == text2[j - 1]
                      table[i - 1][j - 1] + 1
                    else
                      [table[i - 1][j], table[i][j - 1]].max
                    end
    end
  end
  table[rows - 1][cols - 1]
end
```
