---
track: language
language: go
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: totalCost
starter_code: "func totalCost(price, quantity int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# Go: Values and arithmetic — Easy — Shared curriculum

## Learn
Every Go value has a static type, and an expression combines values of compatible types into a new value. `int` and `uint` have an implementation-specific size (32 or 64 bits); `int8` to `int64` have fixed widths. Go has no implicit numeric conversions, so an `int` and an `int64` cannot be mixed in one expression without an explicit conversion. Integer overflow wraps silently; it is defined behaviour, not a panic. A function hands its result back with `return` instead of printing it. Contract: `totalCost(price, quantity int) int` receives two integers from 0 to 1000 and returns the total cost; the largest possible result, 1,000,000, fits in any `int`.

## Common misconception
Do not assume Go converts between numeric types for you. `var a int = 3` and `var b int64 = 4` cannot be multiplied: `a * b` is a compile error (mismatched types `int` and `int64`). Keep both operands the same type, as the signature already does. Also remember that Go rejects a declared but unused local variable, so do not leave scratch variables behind.

## Worked example
```go
hours := 2
minutes := hours * 60
var small int8 = 127
small++
fmt.Println(minutes, small)
```

`:=` infers `int` from the constant, so minutes is 120. The fixed-width `int8` holds -128 to 127, so incrementing 127 silently wraps around to -128: arithmetic that leaves a type's range does not stop the program.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```go
func totalCost(price, quantity int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Both parameters are already `int`, so the product needs no conversion. Return it directly.

## Solutions
### Go
```go
func totalCost(price, quantity int) int {
	return price * quantity
}
```
