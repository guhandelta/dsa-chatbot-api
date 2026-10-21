---
track: language
language: ruby
level: intermediate
order: 9
prerequisites: ruby-path-08-sets
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: final_balance
starter_code: "def final_balance(initial, changes)\n  # Write your solution here.\nend"
test_cases: [{"args": [0, []], "expected": 0}, {"args": [10, [5, -3]], "expected": 12}, {"args": [0, [-5]], "expected": -5}, {"args": [7, [0, 0]], "expected": 7}, {"args": [-2, [2]], "expected": 0}, {"args": [100, [-20, -30, 10]], "expected": 60}]
---
# Ruby: Objects, state, and references — Easy — Shared curriculum

## Learn
An object groups state in instance variables and exposes it through methods. `attr_reader` defines a getter, `attr_writer` a setter and `attr_accessor` both; `account.balance += 5` calls the getter and then the setter `balance=`. Variables hold references, so two names for one object observe the same mutation, while two objects created with `new` have separate state. State created inside a method is fresh on every call.

Contract: `final_balance(initial, changes)` models an account with a balance. Apply each change in order and return the final balance as an `Integer`. `initial` and each change are integers from -1000 to 1000, `changes` has 0 to 100 entries, and negative balances are allowed.

## Common misconception
A class with only `attr_reader :balance` cannot be updated with `account.balance += 5`: Ruby raises `NoMethodError` for the missing `balance=` setter. Inside the class, a bare `balance += 5` treats `balance` as a new local variable that starts as `nil` (so it raises `NoMethodError` for `nil + 5`); write `self.balance += 5` or update `@balance`. Do not keep the account in a global or constant shared across calls; build a new object for each call so tests do not affect each other.

## Worked example
```ruby
class Counter
  attr_accessor :value

  def initialize
    @value = 0
  end
end

counter = Counter.new
alias_ref = counter
alias_ref.value += 1
other = Counter.new
```

`counter.value` is 1 because both names refer to one object. `other.value` is 0 because `new` built a separate object with its own `@value`.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Model an account with a balance field. Apply changes in order and return the final balance. initial and each change are integers from -1000 to 1000; changes has length 0 to 100. Negative balances are allowed.

## Example
Arguments: `[0, []]` → `0`

## Starter code
```ruby
def final_balance(initial, changes)
  # Write your solution here.
end
```

## Approach
Define a small class whose instance holds the balance with both a getter and a setter, create one instance from `initial` inside the method, apply every change in order, and return the balance.

## Solutions
### Ruby
```ruby
class Account
  attr_accessor :balance

  def initialize(balance)
    @balance = balance
  end
end

def final_balance(initial, changes)
  account = Account.new(initial)
  changes.each { |change| account.balance += change }
  account.balance
end
```
