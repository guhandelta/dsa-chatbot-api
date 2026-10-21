---
track: language
language: c
level: intermediate
order: 9
prerequisites: c-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: final_balance
starter_code: "#include <stddef.h>\n\nlong long final_balance(long long initial, const long long* changes, size_t n) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# C: Objects, state, and references — Easy — Shared curriculum

## Learn
A `struct` groups named fields into one object. Use `.` on a struct value and `->` through a pointer to one. C has no methods or classes: behaviour lives in functions that take the struct or a pointer to it. Assigning a struct, or passing it to a function, copies every field (pointer fields are copied as addresses, not what they point to), so a function that must change the caller's object receives a pointer. A struct cannot be compared with `==`.

The contract here: model an account with a `balance` field. Apply each of the `n` values in `changes` in order, starting from `initial`, and return the final balance. `initial` and each change are integers from -1000 to 1000, `n` is 0 to 100, and negative balances are allowed. Create the account state inside the function so that separate calls never share state.

## Common misconception
Passing a struct by value passes a copy. In `void bump(Counter c) { c.value += 1; }` only the function's copy is updated, so the caller's counter does not change; to modify the caller's object, take a `Counter*` and write `c->value += 1`. Likewise do not keep the account in a file-scope (global) variable: it would keep its value between calls and leak state from one test into the next.

## Worked example
```c
typedef struct {
    long long value;
} Counter;

Counter c = {0};
Counter* alias = &c;
alias->value += 1;
Counter copy = c;
copy.value += 10;
```

`c.value` is 1: `alias` points at `c`, so the update goes through to the original. `copy` is a separate object holding its own value 11, and `c` is unaffected by changes to `copy`. Two pointers to one struct see the same mutation; two struct variables have separate state.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length n (0 to 100). Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0` (the C call is `final_balance(0, changes, 0)`)

## Starter code
```c
#include <stddef.h>

long long final_balance(long long initial, const long long* changes, size_t n) {
    // Write your solution here.
    return 0;
}
```

## Approach
Define a small struct with a `balance` field and initialize it from `initial`. Loop over the changes, updating the field for each one (a helper that takes a pointer to the struct keeps the intent clear), then return the field.

## Solutions
### C
```c
#include <stddef.h>

typedef struct {
    long long balance;
} Account;

static void apply_change(Account* account, long long change) {
    account->balance += change;
}

long long final_balance(long long initial, const long long* changes, size_t n) {
    Account account = {initial};
    for (size_t i = 0; i < n; i++) {
        apply_change(&account, changes[i]);
    }
    return account.balance;
}
```
