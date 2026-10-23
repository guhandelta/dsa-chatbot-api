---
track: dsa
difficulty: Medium
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: encoded_length
fn_javascript: encodedLength
fn_typescript: encodedLength
fn_java: encodedLength
fn_cpp: encoded_length
fn_c: encoded_length
fn_rust: encoded_length
fn_go: encodedLength
fn_csharp: EncodedLength
fn_ruby: encoded_length
test_cases: [{"args": [[]], "expected": 0}, {"args": [["a"]], "expected": 3}, {"args": [["ab", "cde"]], "expected": 9}, {"args": [["cat", "lantern"]], "expected": 14}, {"args": [["abcdefghi"]], "expected": 11}, {"args": [["abcdefghij"]], "expected": 13}, {"args": [["hello", "world", "zz"]], "expected": 18}, {"args": [["xxxxxxxxxxxxxxx"]], "expected": 18}, {"args": [["qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"]], "expected": 104}]
---

# Encoded Length — Medium — Arrays and Hashing

## Problem
Each word `w` in the list `words` is encoded as its decimal length, followed by the character `#`, followed by the word itself, written `<len(w)>#<w>`. For example the word `ab` encodes as `2#ab`. Concatenate the encodings of all the words in order and return the total number of characters in that concatenation. Every word is a non-empty string of lowercase ASCII letters. An empty list gives 0. Words can be long, so the length prefix may have more than one digit.

## Example
words = ["cat","lantern"] → 14 ("3#cat" has 5 characters and "7#lantern" has 9)

## Approach
Nothing needs to be built. The encoding of a word has one character per digit of its length, one `#`, and the word's own characters, so it adds digits(len(w)) + 1 + len(w) to the total. Sum that over the list. Time O(total length), space O(1).

## Hints
- A length n has one digit when n < 10, two digits when n < 100, and so on.
- You never need to build the encoded string; the total length is enough.
- Converting the length to text and measuring it counts the digits for you.

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def encoded_length(words):
    return sum(len(str(len(w))) + 1 + len(w) for w in words)
```

### JavaScript
```javascript
function encodedLength(words) {
  let total = 0;
  for (const w of words) total += String(w.length).length + 1 + w.length;
  return total;
}
```

### TypeScript
```typescript
function encodedLength(words: string[]): number {
  let total = 0;
  for (const w of words) total += String(w.length).length + 1 + w.length;
  return total;
}
```

### Java
```java
public long encodedLength(String[] words) {
    long total = 0;
    for (String w : words) {
        total += Integer.toString(w.length()).length() + 1 + w.length();
    }
    return total;
}
```

### C++
```cpp
#include <string>
#include <vector>
long long encoded_length(std::vector<std::string>& words) {
    long long total = 0;
    for (const std::string& w : words) {
        total += (long long)std::to_string(w.size()).size() + 1 + (long long)w.size();
    }
    return total;
}
```

### C
```c
static int digit_count(long long n) {
    int d = 1;
    while (n >= 10) {
        n /= 10;
        d++;
    }
    return d;
}
long long encoded_length(char** words, int wordsSize) {
    long long total = 0;
    for (int i = 0; i < wordsSize; i++) {
        long long len = (long long)strlen(words[i]);
        total += digit_count(len) + 1 + len;
    }
    return total;
}
```

### Rust
```rust
pub fn encoded_length(words: Vec<String>) -> i64 {
    words
        .iter()
        .map(|w| w.len().to_string().len() as i64 + 1 + w.len() as i64)
        .sum()
}
```

### Go
```go
func encodedLength(words []string) int {
	total := 0
	for _, w := range words {
		digits := 1
		for n := len(w); n >= 10; n /= 10 {
			digits++
		}
		total += digits + 1 + len(w)
	}
	return total
}
```

### C#
```csharp
public static long EncodedLength(string[] words)
{
    long total = 0;
    foreach (string w in words)
    {
        total += w.Length.ToString().Length + 1 + w.Length;
    }
    return total;
}
```

### Ruby
```ruby
def encoded_length(words)
  words.sum { |w| w.length.to_s.length + 1 + w.length }
end
```
