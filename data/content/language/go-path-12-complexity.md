---
track: language
language: go
level: expert
order: 12
prerequisites: go-path-11-recursion
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: hasPair
starter_code: "func hasPair(values []int, target int) bool {\n\t// Write your solution here.\n\treturn false\n}"
test_cases: [{"args": [[], 2], "expected": false}, {"args": [[1], 2], "expected": false}, {"args": [[1, 1], 2], "expected": true}, {"args": [[2, 7, 11], 9], "expected": true}, {"args": [[1, 2, 3], 9], "expected": false}, {"args": [[-3, 4], 1], "expected": true}]
---
# Go: Complexity and the DSA bridge — Easy — Shared curriculum

## Learn
Time complexity describes how work grows with input size; space complexity describes additional storage. A single traversal with set operations has expected linear time: map insertion and lookup are expected constant time on average, which is a property of hashing and not a worst-case guarantee. An invariant states what is true about the data structure before each iteration; here, the set holds exactly the values at earlier indices. Contract: `hasPair(values []int, target int) bool` receives 0 to 1000 integers and a target (all between -1000 and 1000) and reports whether two elements at different indices sum to target; use a set to practise one-pass reasoning.

## Common misconception
Two different indices may hold the same value, but one element must never be its own partner: if you insert the current value before checking for its complement, `[1]` with target 2 wrongly succeeds. Check first, insert afterwards. The two partners need not be neighbours in the slice, and either may be negative or zero, so do not compare only adjacent elements or skip non-positive values. A correct result on six tests is evidence, not a proof; explain your invariant and complexity as part of your mastery check.

## Worked example
```go
values := []int{4, 7, 9}
single, nested := 0, 0
for range values {
	single++
}
for range values {
	for range values {
		nested++
	}
}
```

single is 3 (one visit per element) and nested is 9. Nesting a complete second traversal inside each visit creates n × n visits. Count how often operations run, not how many lines the code has.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether two elements at different indices sum to target. Use a set to practice one-pass reasoning. values has length 0 to 1000; elements and target are integers between -1000 and 1000.

## Example
Arguments: `[[], 2]` → `false`

## Starter code
```go
func hasPair(values []int, target int) bool {
	// Write your solution here.
	return false
}
```

## Approach
Walk the slice once. For each value, test whether target minus the value is already in the set; only then add the value to the set.

## Solutions
### Go
```go
func hasPair(values []int, target int) bool {
	seen := make(map[int]struct{})
	for _, v := range values {
		if _, ok := seen[target-v]; ok {
			return true
		}
		seen[v] = struct{}{}
	}
	return false
}
```
