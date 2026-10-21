---
track: language
language: c
level: beginner
order: 1
prerequisites: 
difficulty: Easy
category: Shared curriculum
source: authored
fn_c: total_cost
starter_code: "long long total_cost(long long price, long long quantity) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# C: Values and arithmetic — Easy — Shared curriculum

## Learn
An expression in C has a type, and the type decides how the arithmetic is done. `int` is only guaranteed to hold 16 bits, `long long` at least 64, and the exercise runner passes every integer to your function as a 64-bit `long long`, so declare the parameters and the result as `long long`. Signed integer overflow is undefined behaviour, not a wrap-around, so the width you choose is part of the contract. A function returns its result to the caller with `return`; printing the answer does not satisfy a return-value contract.

The contract here: both arguments are whole numbers from 0 to 1000, and the function returns one `long long`. If either argument is 0 the result is 0.

## Common misconception
Converting to a wider type after the arithmetic does not repair an overflow. In `long long r = a * b;` with `int a` and `int b`, the multiplication is performed in `int` first and only the finished product is widened, so an overflowing product is already undefined behaviour. Widen an operand before the operation: `(long long)a * b`. For `a = b = 100000` that gives 10000000000, which does not fit in a 32-bit `int`. Check with `-Wall -Wextra -fsanitize=undefined`.

## Worked example
```c
long long minutes = 7;
long long seconds = minutes * 60;
```

`seconds` is 420. The integer constant 60 has type `int`; because the other operand is `long long`, it is converted to `long long` and the multiplication happens in 64 bits. Naming the result `seconds` documents what the number means.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000. In C the arguments and the result are `long long`.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```c
long long total_cost(long long price, long long quantity) {
    // Write your solution here.
    return 0;
}
```

## Approach
Multiply the two parameters and return the product. Both operands are already `long long`, so the multiplication cannot overflow for inputs in range (the largest product is 1000000), and the zero cases need no special handling.

## Solutions
### C
```c
long long total_cost(long long price, long long quantity) {
    return price * quantity;
}
```
