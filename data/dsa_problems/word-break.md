---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: dynamic-programming, strings
fn_python: word_break
fn_javascript: wordBreak
fn_typescript: wordBreak
fn_java: wordBreak
fn_cpp: word_break
fn_c: word_break
fn_rust: word_break
fn_go: wordBreak
fn_csharp: WordBreak
fn_ruby: word_break
test_cases: [{"args": ["", ["a"]], "expected": true}, {"args": ["x", ["y"]], "expected": false}, {"args": ["banana", ["ban", "ana"]], "expected": true}, {"args": ["aaaa", ["aa", "a"]], "expected": true}, {"args": ["abcd", ["a", "b", "cd"]], "expected": true}, {"args": ["abcde", ["ab", "abc", "cd"]], "expected": false}, {"args": ["ccccc", ["cc", "ccc"]], "expected": true}, {"args": ["ccccc", ["cc"]], "expected": false}, {"args": ["pineapplepen", ["pine", "apple", "pen"]], "expected": true}]
algorithms: dynamic-programming, strings
---
# Segment a String Into Vocabulary Words — Medium — DP, Strings

## Problem
You get a string `s` of lowercase letters and a non-empty list `vocab` of non-empty words. Decide whether `s` can be cut into one or more consecutive pieces so that every piece equals some entry of `vocab`. An entry may be used as many times as you like, and each piece must be used in order, covering all of `s` with no gaps and no overlaps.

Return `true` if such a cutting exists and `false` otherwise. An empty `s` can be cut into zero pieces, so it returns `true`.

## Example
s = "pineapplepen", vocab = ["pine", "apple", "pen"] → true

## Approach
Let `ok[i]` mean that the first `i` characters of `s` can be cut into vocabulary pieces. Set `ok[0]` to true. For each end position `i`, `ok[i]` is true when some earlier position `j` has `ok[j]` true and the slice `s[j..i)` is a vocabulary entry. Store the entries in a hash set for quick lookup, and only try starts `j` no more than the length of the longest entry before `i`, since longer pieces cannot exist. The answer is `ok[len(s)]`. With `n` characters and longest entry length `L`, this takes O(n·L) lookups, each costing up to O(L) to hash, and O(n) extra space.

## Hints
- Ask of each prefix whether it can be fully explained by pieces.
- Piece lengths are capped by the longest vocabulary entry, which limits how far back each position must look.

## Solutions
*Conventions: Java code sits in `class Solution` after `import java.util.*;`. C++ uses `std::` qualified names and includes its own headers. C includes its own standard headers and uses `char` strings. Rust takes owned `String` and `Vec<String>` values. C# takes an `IList<string>`.*

### Python
```python
def word_break(s, word_dict):
    vocab = set(word_dict)
    longest = max((len(w) for w in vocab), default=0)
    ok = [True] + [False] * len(s)
    for end in range(1, len(s) + 1):
        for start in range(max(0, end - longest), end):
            if ok[start] and s[start:end] in vocab:
                ok[end] = True
                break
    return ok[len(s)]
```

### JavaScript
```javascript
function wordBreak(s, wordDict) {
  const vocab = new Set(wordDict);
  const longest = wordDict.reduce((m, w) => Math.max(m, w.length), 0);
  const ok = new Array(s.length + 1).fill(false);
  ok[0] = true;
  for (let end = 1; end <= s.length; end++) {
    for (let start = Math.max(0, end - longest); start < end; start++) {
      if (ok[start] && vocab.has(s.slice(start, end))) {
        ok[end] = true;
        break;
      }
    }
  }
  return ok[s.length];
}
```

### TypeScript
```typescript
function wordBreak(s: string, wordDict: string[]): boolean {
  const vocab = new Set<string>(wordDict);
  const longest = wordDict.reduce((m, w) => Math.max(m, w.length), 0);
  const ok: boolean[] = new Array(s.length + 1).fill(false);
  ok[0] = true;
  for (let end = 1; end <= s.length; end++) {
    for (let start = Math.max(0, end - longest); start < end; start++) {
      if (ok[start] && vocab.has(s.slice(start, end))) {
        ok[end] = true;
        break;
      }
    }
  }
  return ok[s.length];
}
```

### Java
```java
import java.util.*;

class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        Set<String> vocab = new HashSet<>(wordDict);
        int longest = 0;
        for (String w : wordDict) longest = Math.max(longest, w.length());
        boolean[] ok = new boolean[s.length() + 1];
        ok[0] = true;
        for (int end = 1; end <= s.length(); end++) {
            for (int start = Math.max(0, end - longest); start < end; start++) {
                if (ok[start] && vocab.contains(s.substring(start, end))) {
                    ok[end] = true;
                    break;
                }
            }
        }
        return ok[s.length()];
    }
}
```

### C++
```cpp
#include <algorithm>
#include <string>
#include <unordered_set>
#include <vector>

bool word_break(std::string s, std::vector<std::string>& wordDict) {
    std::unordered_set<std::string> vocab(wordDict.begin(), wordDict.end());
    size_t longest = 0;
    for (const auto& w : wordDict) longest = std::max(longest, w.size());
    std::vector<bool> ok(s.size() + 1, false);
    ok[0] = true;
    for (size_t end = 1; end <= s.size(); end++) {
        size_t start = end > longest ? end - longest : 0;
        for (; start < end; start++) {
            if (ok[start] && vocab.count(s.substr(start, end - start))) {
                ok[end] = true;
                break;
            }
        }
    }
    return ok[s.size()];
}
```

### C
```c
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

bool word_break(char* s, char** wordDict, int wordDictSize) {
    int n = (int)strlen(s);
    bool* ok = calloc(n + 1, sizeof(bool));
    ok[0] = true;
    for (int end = 1; end <= n; end++) {
        for (int w = 0; w < wordDictSize && !ok[end]; w++) {
            int len = (int)strlen(wordDict[w]);
            int start = end - len;
            if (start >= 0 && ok[start] && strncmp(s + start, wordDict[w], len) == 0)
                ok[end] = true;
        }
    }
    bool result = ok[n];
    free(ok);
    return result;
}
```

### Rust
```rust
use std::collections::HashSet;

pub fn word_break(s: String, word_dict: Vec<String>) -> bool {
    let vocab: HashSet<&str> = word_dict.iter().map(|w| w.as_str()).collect();
    let longest = word_dict.iter().map(|w| w.len()).max().unwrap_or(0);
    let n = s.len();
    let mut ok = vec![false; n + 1];
    ok[0] = true;
    for end in 1..=n {
        let first = end.saturating_sub(longest);
        for start in first..end {
            if ok[start] && vocab.contains(&s[start..end]) {
                ok[end] = true;
                break;
            }
        }
    }
    ok[n]
}
```

### Go
```go
func wordBreak(s string, wordDict []string) bool {
	vocab := make(map[string]bool, len(wordDict))
	longest := 0
	for _, w := range wordDict {
		vocab[w] = true
		if len(w) > longest {
			longest = len(w)
		}
	}
	ok := make([]bool, len(s)+1)
	ok[0] = true
	for end := 1; end <= len(s); end++ {
		start := end - longest
		if start < 0 {
			start = 0
		}
		for ; start < end; start++ {
			if ok[start] && vocab[s[start:end]] {
				ok[end] = true
				break
			}
		}
	}
	return ok[len(s)]
}
```

### C#
```csharp
public static class Solution {
    public static bool WordBreak(string s, IList<string> wordDict) {
        var vocab = new HashSet<string>(wordDict);
        int longest = 0;
        foreach (string w in wordDict) longest = Math.Max(longest, w.Length);
        bool[] ok = new bool[s.Length + 1];
        ok[0] = true;
        for (int end = 1; end <= s.Length; end++) {
            for (int start = Math.Max(0, end - longest); start < end; start++) {
                if (ok[start] && vocab.Contains(s.Substring(start, end - start))) {
                    ok[end] = true;
                    break;
                }
            }
        }
        return ok[s.Length];
    }
}
```

### Ruby
```ruby
def word_break(s, word_dict)
  vocab = {}
  word_dict.each { |w| vocab[w] = true }
  longest = word_dict.map(&:length).max || 0
  ok = Array.new(s.length + 1, false)
  ok[0] = true
  (1..s.length).each do |finish|
    ([finish - longest, 0].max...finish).each do |begin_at|
      if ok[begin_at] && vocab.key?(s[begin_at...finish])
        ok[finish] = true
        break
      end
    end
  end
  ok[s.length]
end
```
