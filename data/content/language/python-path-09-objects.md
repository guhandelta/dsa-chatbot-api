---
track: language
language: python
level: intermediate
order: 9
prerequisites: python-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_python: final_balance
starter_code: "def final_balance(initial, changes):\n    # Write your solution here.\n    pass"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# Python: Objects, state, and references — Easy — Shared curriculum

## Learn
An object groups state under named attributes, and a class describes its instances. Updating an attribute changes that object. Two names bound to one object observe the same mutation, while two separately created objects have separate state. A `@dataclass` writes `__init__` and `__repr__` for you.

## Common misconception
A class attribute is shared by every instance; give each object its own state in `__init__`. An object reference is not a deep copy, and a local variable with the same name as an attribute is different storage.

## Worked example
```python
class Counter:
    def __init__(self):
        self.value = 0

counter = Counter()
alias = counter
alias.value += 1
```

counter.value is 1 because both names refer to one object.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```python
def final_balance(initial, changes):
    # Write your solution here.
    pass
```

## Approach
Use the language construct in this lesson, then trace the empty and boundary cases before submitting.

## Solutions
### Python
```python
def final_balance(initial, changes):
    class Account:
        def __init__(self, amount):
            self.balance = amount

    account = Account(initial)
    for change in changes:
        account.balance += change
    return account.balance
```
