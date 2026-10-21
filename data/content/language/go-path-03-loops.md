---
track: language
language: go
level: beginner
order: 3
prerequisites: go-path-02-conditions
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: sumThrough
starter_code: "func sumThrough(n int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [1], "expected": 1}, {"args": [2], "expected": 3}, {"args": [5], "expected": 15}, {"args": [10], "expected": 55}, {"args": [1000], "expected": 500500}]
---
# Go: Loops and accumulation — Easy — Shared curriculum

## Learn
`for` is Go's only loop keyword. It appears as a three-clause loop (`for init; cond; post { }`), a condition-only loop, an infinite loop, and `for ... range`. Since Go 1.22 `for i := range n` counts from 0 to n-1 over an integer. An accumulator stores the result of processing everything visited so far; state what it means before and after each iteration. Contract: `sumThrough(n int) int` receives an integer from 0 to 1000 and returns the sum of 1 through n; for n = 0 the body never runs and the result is 0.

## Common misconception
Off-by-one errors change which values are visited: `i < n` stops one short of `i <= n`. Trace n = 0 and n = 1 by hand. Also beware `:=` inside the loop body: it declares a new variable that hides the outer accumulator, so the outer one never changes (`total := total + i` declares an inner `total`; if the inner one is used the outer `total` stays at 0, and if it is not used the compiler rejects it as declared and not used). Declare the accumulator once before the loop and update it with `=` or `+=`.

## Worked example
```go
result := 1
for i := 0; i < 3; i++ {
	result *= 2
}
total := 0
for i := range 3 {
	total += i
}
```

result goes 1, 2, 4, 8, so it is 8. `range 3` visits 0, 1, 2, so total is 3 (the integer form needs a module that declares Go 1.22 or later). Before each iteration the accumulator holds the result for the values already visited.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of all integers from 1 through n using a loop. n is an integer between 0 and 1000. For n = 0, return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```go
func sumThrough(n int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Start an accumulator at 0, add each value from 1 through n, and return it. The loop condition must include n itself.

## Solutions
### Go
```go
func sumThrough(n int) int {
	total := 0
	for i := 1; i <= n; i++ {
		total += i
	}
	return total
}
```
