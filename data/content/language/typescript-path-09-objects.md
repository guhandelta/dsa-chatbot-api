---
track: language
language: typescript
level: intermediate
order: 9
prerequisites: typescript-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_typescript: finalBalance
starter_code: "function finalBalance(initial: number, changes: readonly number[]): number {\n    // Write your solution here.\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# TypeScript: Objects, state, and references — Easy — Shared curriculum

## Learn
An object groups state under named fields. TypeScript describes its shape with an `interface` or an object type such as `{ balance: number }`, and types are structural: any object with at least the declared fields fits, whatever it was created as. Updating a field changes that object. Two references to one object observe the same mutation, while two separately created objects have separate state. A `readonly` field cannot be assigned through that type, but the modifier exists only in the type checker.

## Common misconception
Create state for each function call rather than sharing a global account across tests. An object reference is not a copy: `const b: { n: number } = a;` shares one object. `readonly` is not a run-time lock: if `a` is typed `{ readonly n: number }` and `b` is a mutable alias of the same object, `b.n = 2` compiles and `a.n` is then 2. A field and a local variable with the same name are different storage locations.

## Worked example
```typescript
interface Counter {
  value: number;
}
const counter: Counter = { value: 0 };
const alias: Counter = counter;
alias.value += 1;
```

`counter.value` is 1. Both references point to one object, so a change through `alias` is visible through `counter`. The `interface` exists only for the compiler; at run time this is an ordinary object literal.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```typescript
function finalBalance(initial: number, changes: readonly number[]): number {
    // Write your solution here.
}
```

## Approach
Use the language construct in this lesson: create an object with a `balance` field set to `initial`, add each change to that field in order, and return the field. Create the object inside the function so each call starts fresh.

## Solutions
### TypeScript
```typescript
interface Account {
    balance: number;
}

function finalBalance(initial: number, changes: readonly number[]): number {
    const account: Account = { balance: initial };
    for (const change of changes) {
        account.balance += change;
    }
    return account.balance;
}
```
