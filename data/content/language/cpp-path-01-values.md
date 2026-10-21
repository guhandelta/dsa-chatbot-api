---
track: language
language: cpp
level: beginner
order: 1
prerequisites:
difficulty: Easy
category: Shared curriculum
source: authored
fn_cpp: total_cost
starter_code: "long long total_cost(long long price, long long quantity) {\n    // Write your solution here.\n    return 0;\n}"
test_cases: [{"args": [3, 4], "expected": 12}, {"args": [0, 5], "expected": 0}, {"args": [9, 0], "expected": 0}, {"args": [1, 1], "expected": 1}, {"args": [1000, 1000], "expected": 1000000}, {"args": [7, 6], "expected": 42}]
---
# C++: Values and arithmetic — Easy — Shared curriculum

## Learn
Every C++ expression has a static type fixed at compile time, and arithmetic is carried out in the types of its operands. Integer values in this course's runner are 64-bit `long long`; choose a type wide enough for the result, because signed integer overflow is undefined behaviour in C++ (unsigned arithmetic wraps instead). A function hands its result back with `return`; printing it is not the same thing.

Contract: `price` and `quantity` are `long long` values from 0 to 1000, and the function returns a `long long`.

## Common misconception
Widening the destination does not widen the arithmetic. In `long long total = a * b;` with `int` operands the product is computed as `int` first and only then converted, so an overflowing product is already undefined behaviour before the assignment happens. Convert one operand before multiplying (`static_cast<long long>(a) * b`) or use a `long long` literal such as `1000LL`. Also remember that integer `/` truncates toward zero and `%` takes the sign of the dividend, so `-7 / 2` is `-3` and `-7 % 2` is `-1`.

## Worked example
```cpp
int hours = 2;
long long ms = hours * 60 * 60 * 1000LL;
```

ms is 7200000. The literal `1000LL` has type `long long`, so the final multiplication is done in 64 bits; `hours * 60 * 60` is still `int` arithmetic, which is safe here only because 7200 is small.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Compute the total cost of quantity items priced at price whole units each. Both inputs are integers from 0 to 1000. Parameters and the result are `long long`.

## Example
Arguments: `[3, 4]` → `12`

## Starter code
```cpp
long long total_cost(long long price, long long quantity) {
    // Write your solution here.
    return 0;
}
```

## Approach
Use the language construct in this lesson. Multiply the two `long long` parameters and return the product.

## Solutions
### C++
```cpp
long long total_cost(long long price, long long quantity) {
    return price * quantity;
}
```
