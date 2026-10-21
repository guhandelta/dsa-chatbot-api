---
track: language
language: go
level: intermediate
order: 8
prerequisites: go-path-07-maps
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: uniqueCount
starter_code: "func uniqueCount(values []int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [[]], "expected": 0}, {"args": [[1]], "expected": 1}, {"args": [[1, 1, 1]], "expected": 1}, {"args": [[1, 2, 3]], "expected": 3}, {"args": [[-1, 0, -1]], "expected": 2}, {"args": [[4, 2, 4, 2, 7]], "expected": 3}]
---
# Go: Sets and equality — Easy — Shared curriculum

## Learn
Go has no built-in set type. The usual set is `map[T]struct{}`: the empty struct takes no space, a key's presence is the only information, and membership is tested with `_, ok := set[x]`. Storing a key that already exists does not add an entry, so `len(set)` is the number of distinct keys. Contract: `uniqueCount(values []int) int` receives 0 to 1000 integers between -1000 and 1000 and returns how many distinct values it contains; the empty slice gives 0.

## Common misconception
If you use `map[int]bool` instead, `len` also counts keys whose stored value is `false`, so a key stored with `false` still adds to the length even though a lookup reads false. Store presence only. Also keep the values as they are: 3 and -3 are different keys, so do not normalise them (for example with an absolute value) before inserting. Also do not depend on the iteration order of a map: ranging over a set may visit the keys in a different order each time.

## Worked example
```go
visited := map[string]struct{}{}
visited["north"] = struct{}{}
visited["north"] = struct{}{}
_, found := visited["north"]
fmt.Println(found, len(visited))
```

found is true and len(visited) is 1: storing the same key twice does not create a second entry. Use a set when only uniqueness or membership matters, and a map when each key also needs a value.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the number of distinct integers in values using a set. values contains 0 to 1000 integers, each between -1000 and 1000.

## Example
Arguments: `[[]]` → `0`

## Starter code
```go
func uniqueCount(values []int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Insert every element into a `map[int]struct{}` and return the map's length.

## Solutions
### Go
```go
func uniqueCount(values []int) int {
	seen := make(map[int]struct{})
	for _, v := range values {
		seen[v] = struct{}{}
	}
	return len(seen)
}
```
