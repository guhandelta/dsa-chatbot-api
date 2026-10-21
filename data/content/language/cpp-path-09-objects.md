---
track: language
language: cpp
level: intermediate
order: 9
prerequisites: cpp-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: final_balance
starter_code: "#include <vector>\n\nlong long final_balance(long long initial, const std::vector<long long>& changes) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# C++: Objects, state, and references — Easy — Shared curriculum

## Learn
A `struct` groups named members; its members are public by default (a `class` is the same except members are private by default). Objects have value semantics: copying a struct copies its members, and the copy is independent. A reference (`Account&`) is an alias for the same object, so a mutation through it is visible under both names. Initialize members deliberately, for example `Account account{initial};`.

Contract: `initial` and each change are `long long` values from -1000 to 1000; `changes` has length 0 to 100; apply the changes in order to an account's balance and return the final balance. Negative balances are allowed.

## Common misconception
Create state for each function call rather than sharing a global account across tests. A plain local `Account account;` leaves a `long long` member uninitialized, and reading it is undefined behaviour; `Account account{};` value-initializes it to zero, and a default member initializer (`long long balance = 0;`) does the same. A copy is not an alias: `Account b = a;` does not share state with `a`, whereas `Account& b = a;` does.

## Worked example
```cpp
struct Counter {
    int value = 0;
};

Counter counter;
Counter& alias = counter;
alias.value += 1;
Counter snapshot = counter;
counter.value += 1;
```

counter.value is 2 and snapshot.value is 1: the alias changed the one object, and the snapshot is a separate copy taken afterwards.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```cpp
#include <vector>

long long final_balance(long long initial, const std::vector<long long>& changes) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Declare a small struct with a balance member, construct one per call, and apply each change in order.

## Solutions
### C++
```cpp
#include <vector>

struct Account {
    long long balance;
};

long long final_balance(long long initial, const std::vector<long long>& changes) {
    Account account{initial};
    for (long long change : changes) {
        account.balance += change;
    }
    return account.balance;
}
```
