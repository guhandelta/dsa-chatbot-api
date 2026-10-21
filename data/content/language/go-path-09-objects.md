---
track: language
language: go
level: intermediate
order: 9
prerequisites: go-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_go: finalBalance
starter_code: "func finalBalance(initial int, changes []int) int {\n\t// Write your solution here.\n\treturn 0\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# Go: Objects, state, and references — Easy — Shared curriculum

## Learn
A struct type groups named fields, and methods attach behaviour to a type. Assigning or passing a struct copies all of its fields, so two struct variables have separate state, unlike two references to one object. A method with a pointer receiver (`func (a *account) apply(...)`) can change the value it is called on; a value receiver works on a copy. If `acc` is an addressable variable, `acc.apply(5)` is shorthand for `(&acc).apply(5)`. Contract: `finalBalance(initial int, changes []int) int` receives an initial balance and 0 to 100 changes (all from -1000 to 1000), applies the changes in order to an account value created for this call, and returns the final balance. Negative balances are allowed. You may declare the type and its method in the same snippet as the function.

## Common misconception
A value receiver changes only a copy. With `func (a account) apply(change int) { a.balance += change }`, calling `acc.apply(5)` leaves `acc` unchanged, so `finalBalance` would always return `initial`. Use a pointer receiver when a method must modify the receiver. Create the state inside the function rather than in a package-level variable shared between calls.

## Worked example
```go
type counter struct{ value int }

func (c *counter) add(n int) { c.value += n }
// inside a function:
c := counter{}
c.add(2)
alias := &c
alias.add(3)
snapshot := c
c.add(1)
fmt.Println(c.value, snapshot.value)
```

After the first add, c.value is 2. alias points to c itself, so alias.add(3) makes c.value 5. snapshot is a copy of the struct, so it keeps 5 while the last add moves c.value to 6. A pointer shares state; a struct assignment copies it.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```go
func finalBalance(initial int, changes []int) int {
	// Write your solution here.
	return 0
}
```

## Approach
Define a struct with a balance field and a pointer-receiver method that adds a change, create one value from initial, apply each change in order, and return its balance.

## Solutions
### Go
```go
type account struct {
	balance int
}

func (a *account) apply(change int) {
	a.balance += change
}

func finalBalance(initial int, changes []int) int {
	acc := account{balance: initial}
	for _, c := range changes {
		acc.apply(c)
	}
	return acc.balance
}
```
