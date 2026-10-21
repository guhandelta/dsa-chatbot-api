---
track: language
language: rust
level: intermediate
order: 9
prerequisites: rust-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_rust: final_balance
starter_code: "fn final_balance(initial: i64, changes: Vec<i64>) -> i64 {\n    // Write your solution here.\n    todo!()\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# Rust: Objects, state, and references — Easy — Shared curriculum

## Learn
A `struct` groups named fields, and an `impl` block attaches methods to it. A method that only reads takes `&self`; one that changes a field takes `&mut self`, and calling it requires the variable to be declared `mut`. Assigning a non-`Copy` struct to another variable moves it, so there is exactly one owner and no accidental aliasing. A `&mut` reference is exclusive: while it is alive no other reference to the same value may be used. Each call to your function builds its own value, so state is never shared between test cases.

Contract: model an account with a balance field. `initial` and each element of `changes` are `i64` integers from -1000 to 1000; `changes` has length 0 to 100. Apply the changes in order and return the final balance as an `i64`. Negative balances are allowed.

## Common misconception
A method that takes `&self` cannot change a field: assigning to `self.value` there is rejected with "cannot assign to `self.value`, which is behind a `&` reference" (E0594). Change it to `&mut self` and declare the caller's variable `mut`. Also remember that two live references to one object are not allowed when one of them is `&mut`; Rust's "aliasing" is checked at compile time, not shared like in garbage-collected languages.

## Worked example
```rust
struct Counter {
    value: i64,
}

impl Counter {
    fn increment(&mut self) {
        self.value += 1;
    }
}

fn main() {
    let mut counter = Counter { value: 0 };
    counter.increment();
    let r = &mut counter;
    r.increment();
    println!("{}", counter.value);
}
```

This prints `2`. `counter` is declared `mut` because `increment` needs `&mut self`. The second increment goes through the exclusive reference `r`; only after `r`'s last use may `counter` be read again, which is why the `println!` comes last.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are `i64` integers from -1000 to 1000; changes is a `Vec<i64>` of length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```rust
fn final_balance(initial: i64, changes: Vec<i64>) -> i64 {
    // Write your solution here.
    todo!()
}
```

## Approach
Define a small struct holding the balance with a method that applies one change, create one account per call from `initial`, apply every change in order, and read the balance at the end.

## Solutions
### Rust
```rust
struct Account {
    balance: i64,
}

impl Account {
    fn new(initial: i64) -> Account {
        Account { balance: initial }
    }

    fn apply(&mut self, change: i64) {
        self.balance += change;
    }
}

fn final_balance(initial: i64, changes: Vec<i64>) -> i64 {
    let mut account = Account::new(initial);
    for change in changes {
        account.apply(change);
    }
    account.balance
}
```
