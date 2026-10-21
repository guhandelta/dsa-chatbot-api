---
track: language
language: go
level: intermediate
order: 7
prerequisites: go-path-06-arrays
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: countTarget
starter_code: "func countTarget(words []string, target string) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [[], "a"], "expected": 0}, {"args": [["a"], "a"], "expected": 1}, {"args": [["a", "b", "a"], "a"], "expected": 2}, {"args": [["a", "b"], "c"], "expected": 0}, {"args": [["x", "x", "x"], "x"], "expected": 3}, {"args": [["aa", "a"], "a"], "expected": 1}]
---
# Go: Maps and frequency counting — Easy — Shared curriculum

## Learn
A Go map `map[K]V` associates keys with values. Reading an absent key returns the value type's zero value, so `freq[w]++` works on a first occurrence (0 + 1). The two-value form `v, ok := m[k]` distinguishes an absent key from a stored zero. A map must be created with `make` or a literal before you write to it. Iteration order is unspecified. Contract: `countTarget(words []string, target string) int` receives 0 to 100 lowercase words and returns how many times target occurs; build a frequency map as your practice technique. A target that never occurred gives 0.

## Common misconception
A nil map can be read but not written: `var m map[string]int` followed by `m["a"]++` panics with an assignment to an entry in a nil map. Create it with `make(map[string]int)` first. Also never rely on the order in which `range` yields map entries. Do not assume every queried word has appeared: a missing key reads as 0.

## Worked example
```go
ages := map[string]int{"Ada": 30}
age, ok := ages["Bob"]
ages["Bob"]++
fmt.Println(age, ok, len(ages))
```

The lookup for Bob returns the zero value and ok false, because Bob is absent. The increment then stores 1 under "Bob", so the map holds two entries. Ada is the key and 30 the value associated with it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Count how often target occurs in words. Build a frequency map as your practice technique. words contains 0 to 100 lowercase English words, each of length 1 to 20; target follows the same rule.

## Example
Arguments: `[[], "a"]` → `0`

## Starter code
```go
func countTarget(words []string, target string) int {
	// Write your solution here.
	return 0
}
```

## Approach
Build a map from word to count in one pass, then return the count stored for target (an absent target reads as 0).

## Solutions
### Go
```go
func countTarget(words []string, target string) int {
	freq := make(map[string]int)
	for _, w := range words {
		freq[w]++
	}
	return freq[target]
}
```
