---
track: language
language: go
level: intermediate
order: 10
prerequisites: go-path-09-objects
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: safeAt
starter_code: "func safeAt(values []int, index, fallback int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [[], 0, 9], "expected": 9}, {"args": [[2, 4], 0, 9], "expected": 2}, {"args": [[2, 4], 1, 9], "expected": 4}, {"args": [[2, 4], 2, 9], "expected": 9}, {"args": [[2, 4], -1, 9], "expected": 9}, {"args": [[0], 0, 5], "expected": 0}]
---
# Go: Validation and failure contracts — Easy — Shared curriculum

## Learn
Validate preconditions before accessing data, and define the behaviour for invalid input explicitly. In Go, evaluating `values[i]` with `i` outside the slice's bounds is a run-time panic. The idiomatic way to report ordinary failures is to return an `error` (or an `ok` flag), reserving `panic` for programming errors; `recover` works only when called directly by a deferred function. This task chooses a fallback value instead, so every input in the contract has a meaningful answer. Contract: `safeAt(values []int, index, fallback int) int` returns `values[index]` when the index is valid and otherwise `fallback`; values has 0 to 100 elements and all integers are between -1000 and 1000.

## Common misconception
Validate both ends of the range: `index < len(values)` alone lets a negative index through, and `index >= 0` alone lets an index at or beyond the length through; either one panics. Do not hide the problem behind a `recover`, which would also swallow unrelated bugs. Remember that the stored value may legitimately be 0, which must not be confused with the fallback.

## Worked example
```go
func positive(value int) (int, error) {
	if value <= 0 {
		return 0, errors.New("expected a positive value")
	}
	return value, nil
}
// inside a function:
n1, err1 := positive(3)
n2, err2 := positive(0)
fmt.Println(n1, err1, n2, err2)
```

Calling positive with 3 returns 3 and a nil error; with 0 it returns 0 and a non-nil error that the caller must check. That is one failure contract: an explicit error result. The exercise below deliberately chooses a fallback instead, so do not copy the error result into it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return values[index] when the index is valid; otherwise return fallback. values has length 0 to 100; all numeric inputs are integers between -1000 and 1000. Do not panic for an invalid index.

## Example
Arguments: `[[], 0, 9]` → `9`

## Starter code
```go
func safeAt(values []int, index, fallback int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Check that index is at least 0 and less than len(values); return fallback when it is not, otherwise return the element.

## Solutions
### Go
```go
func safeAt(values []int, index, fallback int) int {
	if index < 0 || index >= len(values) {
		return fallback
	}
	return values[index]
}
```
