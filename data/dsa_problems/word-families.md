---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: count_word_families
fn_javascript: countWordFamilies
fn_typescript: countWordFamilies
fn_java: countWordFamilies
fn_cpp: count_word_families
fn_c: count_word_families
fn_rust: count_word_families
fn_go: countWordFamilies
fn_csharp: CountWordFamilies
fn_ruby: count_word_families
test_cases: [{"args": [[]], "expected": 0}, {"args": [[""]], "expected": 1}, {"args": [["a"]], "expected": 1}, {"args": [["", ""]], "expected": 1}, {"args": [["ab", "ba", "ab"]], "expected": 1}, {"args": [["abc", "abd", "cab", "bca"]], "expected": 2}, {"args": [["aab", "aba", "abb"]], "expected": 2}, {"args": [["x", "y", "z", "x"]], "expected": 3}, {"args": [["aaaa", "aaa", "aaaaa", "aaaa"]], "expected": 3}, {"args": [["listen", "silent", "enlist", "google", "gogole", "banana"]], "expected": 3}]
---

# Word Families — Medium — Arrays and Hashing

## Problem
Given a list `words` of strings, each made of lowercase ASCII letters (a word may be the empty string), two words belong to the same family when they contain exactly the same letters with the same multiplicities, so that one is a rearrangement of the other. Return how many distinct families appear among `words`. Repeated words count once. An empty list has zero families.

## Example
words = ["stone","tones","notes","sent","rest","tree","reset"] → 5 (the families are {stone, tones, notes}, {sent}, {rest}, {tree} and {reset})

## Approach
Give each word a canonical key that depends only on its multiset of letters, such as the word with its letters sorted. Words in the same family share a key, so the answer is the number of distinct keys, collected in a hash set. Sorting a word costs O(L log L) for word length L; a 26-counter key costs O(L) instead. Time O(total length), space O(number of words).

## Hints
- Two words are in one family exactly when their sorted letters match.
- Sorting is the simplest key; counting the 26 letters into a key is faster for long words.
- A hash set of keys takes care of the deduplication.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def count_word_families(words):
    keys = set()
    for w in words:
        keys.add("".join(sorted(w)))
    return len(keys)
```

### JavaScript
```javascript
function countWordFamilies(words) {
  const keys = new Set();
  for (const w of words) keys.add([...w].sort().join(''));
  return keys.size;
}
```

### TypeScript
```typescript
function countWordFamilies(words: string[]): number {
  const keys = new Set<string>();
  for (const w of words) keys.add([...w].sort().join(''));
  return keys.size;
}
```

### Java
```java
public long countWordFamilies(String[] words) {
    Set<String> keys = new HashSet<>();
    for (String w : words) {
        char[] letters = w.toCharArray();
        Arrays.sort(letters);
        keys.add(new String(letters));
    }
    return keys.size();
}
```

### C++
```cpp
#include <algorithm>
#include <string>
#include <unordered_set>
#include <vector>
long long count_word_families(std::vector<std::string>& words) {
    std::unordered_set<std::string> keys;
    for (std::string w : words) {
        std::sort(w.begin(), w.end());
        keys.insert(w);
    }
    return (long long)keys.size();
}
```

### C
```c
long long count_word_families(char** words, int wordsSize) {
    int (*sig)[26] = calloc(wordsSize > 0 ? wordsSize : 1, sizeof *sig);
    long long families = 0;
    for (int i = 0; i < wordsSize; i++) {
        for (const char* p = words[i]; *p; p++) sig[i][*p - 'a']++;
        bool fresh = true;
        for (int j = 0; j < i && fresh; j++) {
            if (memcmp(sig[i], sig[j], sizeof sig[i]) == 0) fresh = false;
        }
        if (fresh) families++;
    }
    free(sig);
    return families;
}
```

### Rust
```rust
use std::collections::HashSet;
pub fn count_word_families(words: Vec<String>) -> i64 {
    let mut keys: HashSet<[usize; 26]> = HashSet::new();
    for w in words {
        let mut counts = [0usize; 26];
        for b in w.bytes() {
            counts[(b - b'a') as usize] += 1;
        }
        keys.insert(counts);
    }
    keys.len() as i64
}
```

### Go
```go
func countWordFamilies(words []string) int {
	keys := make(map[[26]int]bool)
	for _, w := range words {
		var counts [26]int
		for i := 0; i < len(w); i++ {
			counts[w[i]-'a']++
		}
		keys[counts] = true
	}
	return len(keys)
}
```

### C#
```csharp
public static long CountWordFamilies(string[] words)
{
    var keys = new System.Collections.Generic.HashSet<string>();
    foreach (string w in words)
    {
        char[] letters = w.ToCharArray();
        System.Array.Sort(letters);
        keys.Add(new string(letters));
    }
    return keys.Count;
}
```

### Ruby
```ruby
def count_word_families(words)
  words.map { |w| w.chars.sort.join }.uniq.length
end
```
