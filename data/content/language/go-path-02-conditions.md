---
track: language
language: go
level: beginner
order: 2
prerequisites: go-path-01-values
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: inRange
starter_code: "func inRange(value, low, high int) bool {\n\t// Write your solution here.\n\treturn false\n}"
test_cases: [{"args": [3, 1, 5], "expected": true}, {"args": [1, 1, 5], "expected": true}, {"args": [5, 1, 5], "expected": true}, {"args": [0, 1, 5], "expected": false}, {"args": [6, 1, 5], "expected": false}, {"args": [-2, -2, -2], "expected": true}]
---
# Go: Conditions and boolean logic — Easy — Shared curriculum

## Learn
A condition in Go must have type `bool`; there is no truthiness, so an `int` is never a condition by itself and `if n { ... }` does not compile. Build conditions with comparisons and combine them with `&&` (both must hold) or `||` (either suffices). `&&` evaluates its right operand only when the left operand is true. Inclusive boundaries use `<=` and `>=`; exclusive ones use `<` and `>`. Contract: `inRange(value, low, high int) bool` receives integers from -1000 to 1000 with low <= high and reports whether value lies between low and high, endpoints included.

## Common misconception
A chained mathematical comparison such as `low <= value <= high` does not compile in Go: the first comparison produces a `bool`, which cannot be compared with an `int`. Write both comparisons explicitly and join them with `&&`. Then test each boundary on its own, because swapping `<=` for `<` still passes a mid-range example.

## Worked example
```go
temp := 18
comfortable := temp >= 15 && temp <= 25
if comfortable {
	fmt.Println("comfortable")
}
```

Both comparisons are true, so comfortable is true and the block runs. The condition is already a `bool`, so no extra comparison is needed. Check each endpoint separately when you translate a written rule.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return whether value is between low and high, including both boundaries. low <= high; all values are integers between -1000 and 1000.

## Example
Arguments: `[3, 1, 5]` → `true`

## Starter code
```go
func inRange(value, low, high int) bool {
	// Write your solution here.
	return false
}
```

## Approach
Express the whole rule as one boolean expression and return it. Do not wrap it in an `if` that returns `true` or `false`.

## Solutions
### Go
```go
func inRange(value, low, high int) bool {
	return value >= low && value <= high
}
```
