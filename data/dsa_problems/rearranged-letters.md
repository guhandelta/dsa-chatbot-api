---
track: dsa
difficulty: Easy
source: authored
io_mode: function
algorithms: arrays-and-hashing
fn_python: are_rearrangements
fn_javascript: areRearrangements
fn_typescript: areRearrangements
fn_java: areRearrangements
fn_cpp: are_rearrangements
fn_c: are_rearrangements
fn_rust: are_rearrangements
fn_go: areRearrangements
fn_csharp: AreRearrangements
fn_ruby: are_rearrangements
test_cases: [{"args": ["", ""], "expected": true}, {"args": ["a", ""], "expected": false}, {"args": ["abc", "cba"], "expected": true}, {"args": ["aab", "abb"], "expected": false}, {"args": ["aab", "aba"], "expected": true}, {"args": ["zzzy", "zyzz"], "expected": true}, {"args": ["mississippi", "mississipi"], "expected": false}, {"args": ["abcdefghijklmnopqrstuvwxyz", "zyxwvutsrqponmlkjihgfedcba"], "expected": true}, {"args": ["abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyy"], "expected": false}]
---

# Rearranged Letters — Easy — Arrays and Hashing

## Problem
Given two strings `first` and `second`, return `true` if they are rearrangements of each other: they contain the same letters with the same multiplicities, so one can be reordered into the other. Both strings contain only lowercase ASCII letters `a` through `z`, and either may be empty. Two empty strings are rearrangements of each other. Return `false` otherwise, including whenever the lengths differ.

## Example
first = "lantern", second = "nerlnat" → true (both have two n's and one each of a, e, l, r, t)

## Approach
Count how many times each of the 26 letters occurs in `first`, then subtract the occurrences in `second`. The strings are rearrangements exactly when every resulting difference is zero. Comparing the lengths first is a cheap exit, since strings of different lengths cannot match. Time O(n), space O(1).

## Hints
- Keep an array of 26 counters indexed by `letter - 'a'`.
- Check the lengths before counting; it saves work on mismatches.
- Sorting both strings and comparing also works, at O(n log n).

## Solutions
*Conventions: C++ code uses `std::`-qualified names. Java code sits in `class Solution` with `import java.util.*;`. Go and Rust snippets show any needed package import at the top. C returns a heap array and writes its length to `returnSize`.*

### Python
```python
def are_rearrangements(first, second):
    if len(first) != len(second):
        return False
    counts = [0] * 26
    for ch in first:
        counts[ord(ch) - ord('a')] += 1
    for ch in second:
        counts[ord(ch) - ord('a')] -= 1
    return all(c == 0 for c in counts)
```

### JavaScript
```javascript
function areRearrangements(first, second) {
  if (first.length !== second.length) return false;
  const counts = new Array(26).fill(0);
  for (let i = 0; i < first.length; i++) counts[first.charCodeAt(i) - 97]++;
  for (let i = 0; i < second.length; i++) counts[second.charCodeAt(i) - 97]--;
  return counts.every((c) => c === 0);
}
```

### TypeScript
```typescript
function areRearrangements(first: string, second: string): boolean {
  if (first.length !== second.length) return false;
  const counts: number[] = new Array(26).fill(0);
  for (let i = 0; i < first.length; i++) counts[first.charCodeAt(i) - 97]++;
  for (let i = 0; i < second.length; i++) counts[second.charCodeAt(i) - 97]--;
  return counts.every((c) => c === 0);
}
```

### Java
```java
public boolean areRearrangements(String first, String second) {
    if (first.length() != second.length()) return false;
    int[] counts = new int[26];
    for (int i = 0; i < first.length(); i++) counts[first.charAt(i) - 'a']++;
    for (int i = 0; i < second.length(); i++) counts[second.charAt(i) - 'a']--;
    for (int c : counts) {
        if (c != 0) return false;
    }
    return true;
}
```

### C++
```cpp
#include <string>
bool are_rearrangements(std::string first, std::string second) {
    if (first.size() != second.size()) return false;
    int counts[26] = {0};
    for (char ch : first) counts[ch - 'a']++;
    for (char ch : second) counts[ch - 'a']--;
    for (int c : counts) {
        if (c != 0) return false;
    }
    return true;
}
```

### C
```c
bool are_rearrangements(char* first, char* second) {
    size_t n = strlen(first);
    if (n != strlen(second)) return false;
    int counts[26] = {0};
    for (size_t i = 0; i < n; i++) counts[first[i] - 'a']++;
    for (size_t i = 0; i < n; i++) counts[second[i] - 'a']--;
    for (int i = 0; i < 26; i++) {
        if (counts[i] != 0) return false;
    }
    return true;
}
```

### Rust
```rust
pub fn are_rearrangements(first: String, second: String) -> bool {
    if first.len() != second.len() {
        return false;
    }
    let mut counts = [0i64; 26];
    for b in first.bytes() {
        counts[(b - b'a') as usize] += 1;
    }
    for b in second.bytes() {
        counts[(b - b'a') as usize] -= 1;
    }
    counts.iter().all(|&c| c == 0)
}
```

### Go
```go
func areRearrangements(first string, second string) bool {
	if len(first) != len(second) {
		return false
	}
	var counts [26]int
	for i := 0; i < len(first); i++ {
		counts[first[i]-'a']++
	}
	for i := 0; i < len(second); i++ {
		counts[second[i]-'a']--
	}
	for _, c := range counts {
		if c != 0 {
			return false
		}
	}
	return true
}
```

### C#
```csharp
public static bool AreRearrangements(string first, string second)
{
    if (first.Length != second.Length) return false;
    int[] counts = new int[26];
    foreach (char ch in first) counts[ch - 'a']++;
    foreach (char ch in second) counts[ch - 'a']--;
    foreach (int c in counts)
    {
        if (c != 0) return false;
    }
    return true;
}
```

### Ruby
```ruby
def are_rearrangements(first, second)
  return false if first.length != second.length
  counts = Array.new(26, 0)
  first.each_byte { |b| counts[b - 97] += 1 }
  second.each_byte { |b| counts[b - 97] -= 1 }
  counts.all?(&:zero?)
end
```
