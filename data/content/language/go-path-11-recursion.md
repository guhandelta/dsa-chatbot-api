---
track: language
language: go
level: expert
order: 11
prerequisites: go-path-10-validation
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: digitSum
starter_code: "func digitSum(n int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [0], "expected": 0}, {"args": [7], "expected": 7}, {"args": [10], "expected": 1}, {"args": [123], "expected": 6}, {"args": [909], "expected": 18}, {"args": [1000000], "expected": 1}]
---
# Go: Recursion and base cases — Easy — Shared curriculum

## Learn
A recursive function solves a smaller instance of the same contract. The base case returns an answer without another call, and a decreasing measure explains termination. For a nonnegative integer, `n % 10` is the last decimal digit and `n / 10` (integer division, which truncates toward zero) drops it. Go does not promise tail-call elimination or any fixed recursion depth: goroutine stacks grow, but there is still a maximum size. Contract: `digitSum(n int) int` receives an integer from 0 to 1,000,000 and returns the sum of its decimal digits using recursion; digitSum(0) is 0.

## Common misconception
Check that the recursive input strictly approaches the base case; `digitSum(n)` calling itself with the same n never terminates. The recursive call's result must contribute to the return value instead of being discarded. This input bound keeps the depth at no more than eight calls, but Go does not guarantee a safe depth in general, so use an explicit stack for very deep problems. A recursive closure needs its variable declared first (`var f func(int) int`), whereas a plain function can call itself directly.

## Worked example
```go
func power2(n int) int {
	if n == 0 {
		return 1
	}
	return 2 * power2(n-1)
}
// inside a function:
result := power2(3)
fmt.Println(result)
```

power2(3) calls power2(2), power2(1) and power2(0). The base case returns 1, and each caller doubles what it receives on the way back: 1, 2, 4, 8. The example assumes n is nonnegative.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return the sum of the decimal digits of n using recursion. n is an integer between 0 and 1000000. For n = 0 return 0.

## Example
Arguments: `[0]` → `0`

## Starter code
```go
func digitSum(n int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Handle n == 0 as the base case. Otherwise add the last digit to the result for the number with that digit removed.

## Solutions
### Go
```go
func digitSum(n int) int {
	if n == 0 {
		return 0
	}
	return n%10 + digitSum(n/10)
}
```
