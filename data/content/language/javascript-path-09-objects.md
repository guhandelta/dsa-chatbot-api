---
track: language
language: javascript
level: intermediate
order: 9
prerequisites: javascript-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_javascript: finalBalance
starter_code: "function finalBalance(initial, changes) {\n    // Write your solution here.\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# JavaScript: Objects, state, and references — Easy — Shared curriculum

## Learn
An object groups state under named fields. A class describes instances in Java; JavaScript can create an object directly. Updating a field changes that object. Two references to one object observe the same mutation, while two separately created objects have separate state.

## Common misconception
Create state for each function call rather than sharing a global account across tests. An object reference is not a deep copy. A field and a local variable with the same name are different storage locations.

## Worked example
```javascript
const counter = { value: 0 };
const alias = counter;
alias.value += 1;
```

counter.value is 1. Both references point to one object. Java classes declare their fields and construct instances with new; JavaScript object literals describe their fields directly.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```javascript
function finalBalance(initial, changes) {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson. class Account { int balance; Account(int amount) { balance = amount; } } Account account = new Account(initial); for (int change : changes) { account.balance += change; } return account.balance;

## Solutions
### JavaScript
```javascript
function finalBalance(initial, changes) {
    const account = { balance: initial }; for (const change of changes) { account.balance += change; } return account.balance;
}
```
