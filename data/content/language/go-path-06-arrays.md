---
track: language
language: go
level: intermediate
order: 6
prerequisites: go-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: countAbove
starter_code: "func countAbove(values []int, threshold int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# Go: Arrays and lists — Easy — Shared curriculum

## Learn
A slice `[]int` is a window onto an underlying array, with a length and a capacity. `for i, v := range values` visits each element once; the second variable is a copy of the element, and a nil or empty slice ranges zero times. An array `[N]int` is different: it is a value, copied as a whole when assigned. Contract: `countAbove(values []int, threshold int) int` receives 0 to 1000 integers and an integer threshold (all from -1000 to 1000) and returns how many elements are strictly greater than the threshold, without modifying the slice.

## Common misconception
Assigning a slice to another variable copies only its header; both variables still refer to the same elements, so a write through one is visible through the other. That is why "do not modify values" matters: the caller's data is shared. Assigning to the range variable `v` changes only a copy, not the slice. Strictly greater excludes equal values.

## Worked example
```go
arr := [2]int{3, 8}
arrCopy := arr
arrCopy[0] = 5
sl := []int{3, 8}
slAlias := sl
slAlias[0] = 5
```

arr[0] is still 3 because the array was copied as a whole, but sl[0] is now 5 because slAlias shares sl's elements. To get an independent slice, allocate a new one and use `copy`, or `slices.Clone`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```go
func countAbove(values []int, threshold int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Range over the slice, compare each element with the threshold using `>`, and count the matches.

## Solutions
### Go
```go
func countAbove(values []int, threshold int) int {
	count := 0
	for _, v := range values {
		if v > threshold {
			count++
		}
	}
	return count
}
```
