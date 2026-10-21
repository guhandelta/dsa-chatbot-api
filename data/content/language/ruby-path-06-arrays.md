---
track: language
language: ruby
level: intermediate
order: 6
prerequisites: ruby-path-05-strings
difficulty: Easy
category: Shared curriculum
source: authored
fn_ruby: count_above
starter_code: "def count_above(values, threshold)\n  # Write your solution here.\nend"
test_cases: [{"args": [[], 0], "expected": 0}, {"args": [[1, 2, 3], 2], "expected": 1}, {"args": [[2, 2], 2], "expected": 0}, {"args": [[-3, -1, 0], -2], "expected": 2}, {"args": [[5], 0], "expected": 1}, {"args": [[1, 4, 4, 7], 3], "expected": 3}]
---
# Ruby: Arrays and lists — Easy — Shared curriculum

## Learn
An `Array` is a dynamic, ordered, index-based collection that grows automatically and can hold values of different types. Indexes start at 0, negative indexes count from the end, and traversal visits each element once. Distinguish the element from its index, and a new copy from another reference to the same array: assignment and argument passing copy references, `dup` makes a shallow copy. Methods ending in `!` (`sort!`, `select!`, `map!`) mutate the receiver, and some, such as `select!`, return `nil` when nothing changed; the non-bang versions return new arrays.

Contract: `count_above(values, threshold)` receives an array of 0 to 1000 integers and an integer threshold (all from -1000 to 1000) and returns how many elements are strictly greater than `threshold`. The caller's array must not be modified.

## Common misconception
Because arguments are references, a bang method called on `values` changes the caller's array: `values.select! { ... }` or `values.sort!` inside your method is visible after it returns, which this contract forbids. Use the non-bang forms or a plain traversal. Also remember "strictly greater" excludes equal values, and the empty array gives 0.

## Worked example
```ruby
scores = [3, 8]
copy = scores.dup
copy[0] = 5
alias_ref = scores
alias_ref[1] = 9
```

`scores[0]` is still 3 because `dup` made a separate array, but `scores[1]` is now 9 because `alias_ref` and `scores` refer to the same array. `dup` is shallow: nested arrays inside would still be shared.

## Mastery check
Explain the input and return contract, trace one normal case and one boundary case, then implement the exercise. Passing the tests is a checkpoint; also explain why your implementation works.

## Problem
Return how many elements in values are strictly greater than threshold. values has length 0 to 1000; its elements and threshold are integers from -1000 to 1000. Do not modify values.

## Example
Arguments: `[[], 0]` → `0`

## Starter code
```ruby
def count_above(values, threshold)
  # Write your solution here.
end
```

## Approach
Walk the array once without changing it, count the elements for which the strict comparison with the threshold is true, and return the count.

## Solutions
### Ruby
```ruby
def count_above(values, threshold)
  count = 0
  values.each do |value|
    count += 1 if value > threshold
  end
  count
end
```
