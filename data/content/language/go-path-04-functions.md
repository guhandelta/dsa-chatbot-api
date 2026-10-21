---
track: language
language: go
level: beginner
order: 4
prerequisites: go-path-03-loops
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: distance
starter_code: "func distance(a, b int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [2, 5], "expected": 3}, {"args": [5, 2], "expected": 3}, {"args": [0, 0], "expected": 0}, {"args": [-3, 4], "expected": 7}, {"args": [-8, -2], "expected": 6}, {"args": [-1000, 1000], "expected": 2000}]
---
# Go: Functions and contracts — Easy — Shared curriculum

## Learn
A function declaration lists each parameter's type and the result type; adjacent parameters can share a type, as in `func distance(a, b int) int`. Go passes every argument by value, so a parameter is a local copy of the caller's value. `return` ends the current call and hands back the result; printing does not satisfy a return-value contract. Functions can also return several values, with an `error` conventionally last. Contract: `distance(a, b int) int` receives integer positions from -1000 to 1000 and returns the nonnegative distance between them.

## Common misconception
Reassigning a parameter inside a function never changes the caller's variable, because the parameter is a copy. Also, Go has no built-in integer absolute value: `math.Abs` takes and returns `float64`, so `var x int = math.Abs(-3)` does not compile. Decide the order of the two values with a comparison. Negative positions still have a nonnegative distance.

## Worked example
```go
func addTax(price int) int {
	price += 5
	return price
}
// inside a function:
cost := 20
total := addTax(cost)
fmt.Println(total, cost)
```

total is 25, but cost is still 20: the call received a copy of cost, and the `+=` changed only that copy. The result reaches the caller through `return`. The exercise runner calls your function directly, so you do not need a `main` function.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the nonnegative distance between integer positions a and b. Inputs are between -1000 and 1000. Keep the supplied function signature and return an integer.

## Example
Arguments: `[2, 5]` → `3`

## Starter code
```go
func distance(a, b int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Subtract the smaller position from the larger one, choosing the order with a comparison, and return the result.

## Solutions
### Go
```go
func distance(a, b int) int {
	if a > b {
		return a - b
	}
	return b - a
}
```
