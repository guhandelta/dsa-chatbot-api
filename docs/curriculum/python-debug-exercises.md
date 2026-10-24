# Python Debug Exercises

A training corpus of 300 Python debugging exercises for retrieval-augmented tutoring. Each record contains a learner-facing failure, an editorial diagnosis, a corrected implementation, and regression guidance. The corrected code is included for training and evaluation data; production challenge responses must strip it before serving.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: output tracing, state tracing, contracts, types, collections, recursion, complexity, async, concurrency, security, transactions, and data model invariants


## PY-E-001: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_1(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_1(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_1([1, 2, 3]) == 6
assert total_1([]) == 0
```


## PY-E-002: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_2(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_2(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_2(['a', '', 'b']) == 2
assert count_2([]) == 0
```


## PY-E-003: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_3(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_3(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_3(0) == 'present'
assert label_3(None) == 'missing'
```


## PY-E-004: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_4(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_4(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_4(7) == 'age=7'
```


## PY-E-005: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_5(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_5(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_5([-1, -2, 3]) == [3]
assert remove_5([1, 2]) == [1, 2]
```


## PY-E-006: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_6(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_6(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_6('Hi,  there!') == ['Hi', 'there']
```


## PY-E-007: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_7(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_7(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_7('a') == ['a']
assert add_7('b') == ['b']
```


## PY-E-008: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_8(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_8(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_8({'a': 1}, 'b') is None
assert lookup_8({'a': 1}, 'a') == 1
```


## PY-E-009: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_9(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_9(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_9(5)
assert not valid_9(-1)
assert not valid_9(11)
```


## PY-E-010: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_10(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_10(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_10([3, 1, 2]) == [1, 2, 3]
```


## PY-E-011: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_11(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_11(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_11([1, 2, 3]) == 6
assert total_11([]) == 0
```


## PY-E-012: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_12(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_12(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_12(['a', '', 'b']) == 2
assert count_12([]) == 0
```


## PY-E-013: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_13(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_13(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_13(0) == 'present'
assert label_13(None) == 'missing'
```


## PY-E-014: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_14(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_14(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_14(7) == 'age=7'
```


## PY-E-015: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_15(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_15(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_15([-1, -2, 3]) == [3]
assert remove_15([1, 2]) == [1, 2]
```


## PY-E-016: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_16(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_16(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_16('Hi,  there!') == ['Hi', 'there']
```


## PY-E-017: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_17(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_17(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_17('a') == ['a']
assert add_17('b') == ['b']
```


## PY-E-018: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_18(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_18(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_18({'a': 1}, 'b') is None
assert lookup_18({'a': 1}, 'a') == 1
```


## PY-E-019: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_19(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_19(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_19(5)
assert not valid_19(-1)
assert not valid_19(11)
```


## PY-E-020: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_20(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_20(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_20([3, 1, 2]) == [1, 2, 3]
```


## PY-E-021: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_21(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_21(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_21([1, 2, 3]) == 6
assert total_21([]) == 0
```


## PY-E-022: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_22(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_22(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_22(['a', '', 'b']) == 2
assert count_22([]) == 0
```


## PY-E-023: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_23(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_23(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_23(0) == 'present'
assert label_23(None) == 'missing'
```


## PY-E-024: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_24(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_24(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_24(7) == 'age=7'
```


## PY-E-025: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_25(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_25(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_25([-1, -2, 3]) == [3]
assert remove_25([1, 2]) == [1, 2]
```


## PY-E-026: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_26(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_26(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_26('Hi,  there!') == ['Hi', 'there']
```


## PY-E-027: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_27(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_27(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_27('a') == ['a']
assert add_27('b') == ['b']
```


## PY-E-028: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_28(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_28(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_28({'a': 1}, 'b') is None
assert lookup_28({'a': 1}, 'a') == 1
```


## PY-E-029: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_29(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_29(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_29(5)
assert not valid_29(-1)
assert not valid_29(11)
```


## PY-E-030: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_30(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_30(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_30([3, 1, 2]) == [1, 2, 3]
```


## PY-E-031: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_31(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_31(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_31([1, 2, 3]) == 6
assert total_31([]) == 0
```


## PY-E-032: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_32(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_32(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_32(['a', '', 'b']) == 2
assert count_32([]) == 0
```


## PY-E-033: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_33(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_33(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_33(0) == 'present'
assert label_33(None) == 'missing'
```


## PY-E-034: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_34(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_34(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_34(7) == 'age=7'
```


## PY-E-035: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_35(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_35(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_35([-1, -2, 3]) == [3]
assert remove_35([1, 2]) == [1, 2]
```


## PY-E-036: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_36(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_36(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_36('Hi,  there!') == ['Hi', 'there']
```


## PY-E-037: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_37(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_37(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_37('a') == ['a']
assert add_37('b') == ['b']
```


## PY-E-038: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_38(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_38(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_38({'a': 1}, 'b') is None
assert lookup_38({'a': 1}, 'a') == 1
```


## PY-E-039: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_39(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_39(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_39(5)
assert not valid_39(-1)
assert not valid_39(11)
```


## PY-E-040: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_40(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_40(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_40([3, 1, 2]) == [1, 2, 3]
```


## PY-E-041: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_41(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_41(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_41([1, 2, 3]) == 6
assert total_41([]) == 0
```


## PY-E-042: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_42(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_42(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_42(['a', '', 'b']) == 2
assert count_42([]) == 0
```


## PY-E-043: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_43(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_43(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_43(0) == 'present'
assert label_43(None) == 'missing'
```


## PY-E-044: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_44(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_44(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_44(7) == 'age=7'
```


## PY-E-045: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_45(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_45(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_45([-1, -2, 3]) == [3]
assert remove_45([1, 2]) == [1, 2]
```


## PY-E-046: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_46(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_46(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_46('Hi,  there!') == ['Hi', 'there']
```


## PY-E-047: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_47(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_47(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_47('a') == ['a']
assert add_47('b') == ['b']
```


## PY-E-048: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_48(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_48(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_48({'a': 1}, 'b') is None
assert lookup_48({'a': 1}, 'a') == 1
```


## PY-E-049: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_49(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_49(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_49(5)
assert not valid_49(-1)
assert not valid_49(11)
```


## PY-E-050: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_50(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_50(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_50([3, 1, 2]) == [1, 2, 3]
```


## PY-E-051: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_51(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_51(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_51([1, 2, 3]) == 6
assert total_51([]) == 0
```


## PY-E-052: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_52(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_52(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_52(['a', '', 'b']) == 2
assert count_52([]) == 0
```


## PY-E-053: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_53(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_53(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_53(0) == 'present'
assert label_53(None) == 'missing'
```


## PY-E-054: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_54(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_54(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_54(7) == 'age=7'
```


## PY-E-055: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_55(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_55(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_55([-1, -2, 3]) == [3]
assert remove_55([1, 2]) == [1, 2]
```


## PY-E-056: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_56(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_56(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_56('Hi,  there!') == ['Hi', 'there']
```


## PY-E-057: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_57(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_57(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_57('a') == ['a']
assert add_57('b') == ['b']
```


## PY-E-058: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_58(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_58(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_58({'a': 1}, 'b') is None
assert lookup_58({'a': 1}, 'a') == 1
```


## PY-E-059: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_59(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_59(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_59(5)
assert not valid_59(-1)
assert not valid_59(11)
```


## PY-E-060: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_60(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_60(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_60([3, 1, 2]) == [1, 2, 3]
```


## PY-E-061: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_61(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_61(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_61([1, 2, 3]) == 6
assert total_61([]) == 0
```


## PY-E-062: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_62(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_62(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_62(['a', '', 'b']) == 2
assert count_62([]) == 0
```


## PY-E-063: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_63(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_63(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_63(0) == 'present'
assert label_63(None) == 'missing'
```


## PY-E-064: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_64(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_64(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_64(7) == 'age=7'
```


## PY-E-065: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_65(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_65(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_65([-1, -2, 3]) == [3]
assert remove_65([1, 2]) == [1, 2]
```


## PY-E-066: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_66(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_66(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_66('Hi,  there!') == ['Hi', 'there']
```


## PY-E-067: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_67(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_67(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_67('a') == ['a']
assert add_67('b') == ['b']
```


## PY-E-068: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_68(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_68(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_68({'a': 1}, 'b') is None
assert lookup_68({'a': 1}, 'a') == 1
```


## PY-E-069: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_69(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_69(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_69(5)
assert not valid_69(-1)
assert not valid_69(11)
```


## PY-E-070: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_70(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_70(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_70([3, 1, 2]) == [1, 2, 3]
```


## PY-E-071: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_71(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_71(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_71([1, 2, 3]) == 6
assert total_71([]) == 0
```


## PY-E-072: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_72(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_72(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_72(['a', '', 'b']) == 2
assert count_72([]) == 0
```


## PY-E-073: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_73(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_73(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_73(0) == 'present'
assert label_73(None) == 'missing'
```


## PY-E-074: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_74(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_74(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_74(7) == 'age=7'
```


## PY-E-075: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_75(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_75(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_75([-1, -2, 3]) == [3]
assert remove_75([1, 2]) == [1, 2]
```


## PY-E-076: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_76(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_76(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_76('Hi,  there!') == ['Hi', 'there']
```


## PY-E-077: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_77(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_77(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_77('a') == ['a']
assert add_77('b') == ['b']
```


## PY-E-078: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_78(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_78(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_78({'a': 1}, 'b') is None
assert lookup_78({'a': 1}, 'a') == 1
```


## PY-E-079: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_79(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_79(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_79(5)
assert not valid_79(-1)
assert not valid_79(11)
```


## PY-E-080: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_80(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_80(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_80([3, 1, 2]) == [1, 2, 3]
```


## PY-E-081: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_81(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_81(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_81([1, 2, 3]) == 6
assert total_81([]) == 0
```


## PY-E-082: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_82(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_82(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_82(['a', '', 'b']) == 2
assert count_82([]) == 0
```


## PY-E-083: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_83(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_83(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_83(0) == 'present'
assert label_83(None) == 'missing'
```


## PY-E-084: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_84(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_84(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_84(7) == 'age=7'
```


## PY-E-085: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_85(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_85(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_85([-1, -2, 3]) == [3]
assert remove_85([1, 2]) == [1, 2]
```


## PY-E-086: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_86(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_86(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_86('Hi,  there!') == ['Hi', 'there']
```


## PY-E-087: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_87(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_87(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_87('a') == ['a']
assert add_87('b') == ['b']
```


## PY-E-088: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_88(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_88(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_88({'a': 1}, 'b') is None
assert lookup_88({'a': 1}, 'a') == 1
```


## PY-E-089: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_89(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_89(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_89(5)
assert not valid_89(-1)
assert not valid_89(11)
```


## PY-E-090: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_90(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_90(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_90([3, 1, 2]) == [1, 2, 3]
```


## PY-E-091: off-by-one range

- Difficulty: Easy
- Perspective: Output tracing
- Concept: off-by-one range
- Symptom: The sum is one too small.
- Diagnostic goal: Trace the inclusive upper boundary.

### Buggy code

```python
def total_91(values):
    total = 0
    for i in range(len(values) - 1):
        total += values[i]
    return total
```

### Expected diagnosis

The loop stops before the last valid index because the range endpoint is len(values) - 1.

### Corrected code

```python
def total_91(values):
    total = 0
    for i in range(len(values)):
        total += values[i]
    return total
```

### Regression tests

```python
assert total_91([1, 2, 3]) == 6
assert total_91([]) == 0
```


## PY-E-092: accumulator reset

- Difficulty: Easy
- Perspective: State tracing
- Concept: accumulator reset
- Symptom: Only the last item is counted.
- Diagnostic goal: Track where the accumulator is created.

### Buggy code

```python
def count_92(words):
    for word in words:
        count = 0
        if word:
            count += 1
    return count
```

### Expected diagnosis

The accumulator is re-created inside the loop, so earlier results are discarded.

### Corrected code

```python
def count_92(words):
    count = 0
    for word in words:
        if word:
            count += 1
    return count
```

### Regression tests

```python
assert count_92(['a', '', 'b']) == 2
assert count_92([]) == 0
```


## PY-E-093: truthiness loses zero

- Difficulty: Easy
- Perspective: Boundary analysis
- Concept: truthiness loses zero
- Symptom: A valid zero is treated as missing.
- Diagnostic goal: Distinguish falsy values from absent values.

### Buggy code

```python
def label_93(count):
    return 'present' if count else 'missing'
```

### Expected diagnosis

Zero is falsy in Python, but it can still be a valid value.

### Corrected code

```python
def label_93(count):
    return 'missing' if count is None else 'present'
```

### Regression tests

```python
assert label_93(0) == 'present'
assert label_93(None) == 'missing'
```


## PY-E-094: string concatenation

- Difficulty: Easy
- Perspective: Type reasoning
- Concept: string concatenation
- Symptom: The function raises TypeError for numeric input.
- Diagnostic goal: Identify the incompatible operand types.

### Buggy code

```python
def describe_94(age):
    return 'age=' + age
```

### Expected diagnosis

The + operator does not implicitly convert an integer to a string.

### Corrected code

```python
def describe_94(age):
    return f'age={age}'
```

### Regression tests

```python
assert describe_94(7) == 'age=7'
```


## PY-E-095: list mutation during iteration

- Difficulty: Easy
- Perspective: Collection inspection
- Concept: list mutation during iteration
- Symptom: Some matching values remain in the list.
- Diagnostic goal: Explain why indexes shift after deletion.

### Buggy code

```python
def remove_95(values):
    for value in values:
        if value < 0:
            values.remove(value)
    return values
```

### Expected diagnosis

Removing an element shifts later elements left while the iterator advances, so adjacent matches can be skipped.

### Corrected code

```python
def remove_95(values):
    return [value for value in values if value >= 0]
```

### Regression tests

```python
assert remove_95([-1, -2, 3]) == [3]
assert remove_95([1, 2]) == [1, 2]
```


## PY-E-096: split delimiter

- Difficulty: Easy
- Perspective: String reasoning
- Concept: split delimiter
- Symptom: The final token still contains punctuation.
- Diagnostic goal: Check the delimiter and the normalization order.

### Buggy code

```python
def words_96(text):
    return text.split(' ')
```

### Expected diagnosis

Splitting on one literal space preserves punctuation and can create empty tokens.

### Corrected code

```python
def words_96(text):
    return [word.strip('.,!?') for word in text.split() if word.strip('.,!?')]
```

### Regression tests

```python
assert words_96('Hi,  there!') == ['Hi', 'there']
```


## PY-E-097: mutable default argument

- Difficulty: Easy
- Perspective: Function contract
- Concept: mutable default argument
- Symptom: Data from an earlier call appears in a later call.
- Diagnostic goal: Find state that survives between calls.

### Buggy code

```python
def add_97(item, bucket=[]):
    bucket.append(item)
    return bucket
```

### Expected diagnosis

Default arguments are evaluated once when the function is defined, so the same list is reused.

### Corrected code

```python
def add_97(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### Regression tests

```python
assert add_97('a') == ['a']
assert add_97('b') == ['b']
```


## PY-E-098: broad exception

- Difficulty: Easy
- Perspective: Exception reasoning
- Concept: broad exception
- Symptom: A programming error is silently converted into a default.
- Diagnostic goal: Separate expected input failure from programmer failure.

### Buggy code

```python
def lookup_98(mapping, key):
    try:
        return mapping[key]
    except Exception:
        return None
```

### Expected diagnosis

Catching Exception hides unrelated errors such as a misspelled variable or broken method.

### Corrected code

```python
def lookup_98(mapping, key):
    try:
        return mapping[key]
    except KeyError:
        return None
```

### Regression tests

```python
assert lookup_98({'a': 1}, 'b') is None
assert lookup_98({'a': 1}, 'a') == 1
```


## PY-E-099: wrong connective

- Difficulty: Easy
- Perspective: Boolean logic
- Concept: wrong connective
- Symptom: The filter accepts values outside the intended interval.
- Diagnostic goal: Translate the natural-language condition literally.

### Buggy code

```python
def valid_99(value):
    return value >= 0 or value <= 10
```

### Expected diagnosis

Every number satisfies at least one of those comparisons; a bounded interval requires and.

### Corrected code

```python
def valid_99(value):
    return 0 <= value <= 10
```

### Regression tests

```python
assert valid_99(5)
assert not valid_99(-1)
assert not valid_99(11)
```


## PY-E-100: in-place versus returned value

- Difficulty: Easy
- Perspective: API contract
- Concept: in-place versus returned value
- Symptom: The caller receives None instead of a sorted list.
- Diagnostic goal: Check whether the method mutates or returns a new value.

### Buggy code

```python
def ordered_100(values):
    return values.sort()
```

### Expected diagnosis

list.sort mutates the list and returns None; sorted returns a new ordered list.

### Corrected code

```python
def ordered_100(values):
    return sorted(values)
```

### Regression tests

```python
assert ordered_100([3, 1, 2]) == [1, 2, 3]
```


## PY-M-001: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_1(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_1(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_1({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-002: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_2(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_2(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_2([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-003: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_3(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_3(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_3(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-004: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_4(value):
    print(value)
    return countdown_4(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_4(value):
    if value <= 0:
        return []
    return [value] + countdown_4(value - 1)
```

### Regression tests

```python
assert countdown_4(3) == [3, 2, 1]
assert countdown_4(0) == []
```


## PY-M-005: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_5(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_5(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_5([3, 1, 2]) == [1, 2, 3]
```


## PY-M-006: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_6(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_6(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-007: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_7(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_7(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_7([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-008: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_8(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_8(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_8([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-009: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_9(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_9(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_9([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-010: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_10(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_10(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_10({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-011: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_11(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_11(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_11([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-012: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_12(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_12(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_12(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-013: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_13(value):
    print(value)
    return countdown_13(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_13(value):
    if value <= 0:
        return []
    return [value] + countdown_13(value - 1)
```

### Regression tests

```python
assert countdown_13(3) == [3, 2, 1]
assert countdown_13(0) == []
```


## PY-M-014: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_14(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_14(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_14([3, 1, 2]) == [1, 2, 3]
```


## PY-M-015: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_15(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_15(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-016: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_16(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_16(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_16([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-017: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_17(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_17(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_17([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-018: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_18(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_18(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_18([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-019: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_19(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_19(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_19({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-020: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_20(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_20(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_20([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-021: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_21(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_21(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_21(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-022: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_22(value):
    print(value)
    return countdown_22(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_22(value):
    if value <= 0:
        return []
    return [value] + countdown_22(value - 1)
```

### Regression tests

```python
assert countdown_22(3) == [3, 2, 1]
assert countdown_22(0) == []
```


## PY-M-023: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_23(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_23(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_23([3, 1, 2]) == [1, 2, 3]
```


## PY-M-024: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_24(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_24(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-025: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_25(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_25(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_25([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-026: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_26(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_26(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_26([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-027: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_27(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_27(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_27([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-028: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_28(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_28(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_28({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-029: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_29(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_29(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_29([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-030: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_30(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_30(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_30(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-031: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_31(value):
    print(value)
    return countdown_31(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_31(value):
    if value <= 0:
        return []
    return [value] + countdown_31(value - 1)
```

### Regression tests

```python
assert countdown_31(3) == [3, 2, 1]
assert countdown_31(0) == []
```


## PY-M-032: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_32(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_32(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_32([3, 1, 2]) == [1, 2, 3]
```


## PY-M-033: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_33(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_33(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-034: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_34(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_34(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_34([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-035: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_35(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_35(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_35([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-036: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_36(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_36(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_36([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-037: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_37(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_37(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_37({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-038: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_38(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_38(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_38([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-039: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_39(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_39(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_39(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-040: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_40(value):
    print(value)
    return countdown_40(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_40(value):
    if value <= 0:
        return []
    return [value] + countdown_40(value - 1)
```

### Regression tests

```python
assert countdown_40(3) == [3, 2, 1]
assert countdown_40(0) == []
```


## PY-M-041: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_41(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_41(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_41([3, 1, 2]) == [1, 2, 3]
```


## PY-M-042: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_42(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_42(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-043: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_43(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_43(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_43([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-044: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_44(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_44(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_44([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-045: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_45(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_45(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_45([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-046: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_46(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_46(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_46({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-047: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_47(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_47(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_47([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-048: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_48(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_48(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_48(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-049: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_49(value):
    print(value)
    return countdown_49(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_49(value):
    if value <= 0:
        return []
    return [value] + countdown_49(value - 1)
```

### Regression tests

```python
assert countdown_49(3) == [3, 2, 1]
assert countdown_49(0) == []
```


## PY-M-050: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_50(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_50(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_50([3, 1, 2]) == [1, 2, 3]
```


## PY-M-051: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_51(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_51(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-052: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_52(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_52(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_52([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-053: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_53(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_53(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_53([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-054: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_54(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_54(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_54([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-055: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_55(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_55(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_55({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-056: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_56(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_56(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_56([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-057: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_57(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_57(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_57(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-058: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_58(value):
    print(value)
    return countdown_58(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_58(value):
    if value <= 0:
        return []
    return [value] + countdown_58(value - 1)
```

### Regression tests

```python
assert countdown_58(3) == [3, 2, 1]
assert countdown_58(0) == []
```


## PY-M-059: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_59(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_59(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_59([3, 1, 2]) == [1, 2, 3]
```


## PY-M-060: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_60(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_60(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-061: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_61(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_61(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_61([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-062: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_62(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_62(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_62([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-063: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_63(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_63(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_63([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-064: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_64(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_64(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_64({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-065: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_65(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_65(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_65([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-066: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_66(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_66(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_66(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-067: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_67(value):
    print(value)
    return countdown_67(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_67(value):
    if value <= 0:
        return []
    return [value] + countdown_67(value - 1)
```

### Regression tests

```python
assert countdown_67(3) == [3, 2, 1]
assert countdown_67(0) == []
```


## PY-M-068: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_68(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_68(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_68([3, 1, 2]) == [1, 2, 3]
```


## PY-M-069: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_69(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_69(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-070: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_70(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_70(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_70([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-071: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_71(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_71(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_71([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-072: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_72(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_72(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_72([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-073: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_73(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_73(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_73({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-074: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_74(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_74(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_74([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-075: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_75(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_75(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_75(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-076: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_76(value):
    print(value)
    return countdown_76(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_76(value):
    if value <= 0:
        return []
    return [value] + countdown_76(value - 1)
```

### Regression tests

```python
assert countdown_76(3) == [3, 2, 1]
assert countdown_76(0) == []
```


## PY-M-077: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_77(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_77(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_77([3, 1, 2]) == [1, 2, 3]
```


## PY-M-078: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_78(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_78(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-079: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_79(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_79(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_79([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-080: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_80(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_80(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_80([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-081: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_81(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_81(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_81([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-082: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_82(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_82(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_82({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-083: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_83(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_83(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_83([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-084: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_84(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_84(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_84(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-085: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_85(value):
    print(value)
    return countdown_85(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_85(value):
    if value <= 0:
        return []
    return [value] + countdown_85(value - 1)
```

### Regression tests

```python
assert countdown_85(3) == [3, 2, 1]
assert countdown_85(0) == []
```


## PY-M-086: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_86(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_86(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_86([3, 1, 2]) == [1, 2, 3]
```


## PY-M-087: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_87(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_87(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-088: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_88(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_88(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_88([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-089: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_89(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_89(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_89([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-090: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_90(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_90(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_90([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-091: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_91(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_91(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_91({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-M-092: generator exhaustion

- Difficulty: Medium
- Perspective: Iterator protocol
- Concept: generator exhaustion
- Symptom: The second consumer sees no values.
- Diagnostic goal: Track the lifetime and consumption of the iterator.

### Buggy code

```python
def pair_92(values):
    items = (value * 2 for value in values)
    first = list(items)
    second = list(items)
    return first, second
```

### Expected diagnosis

A generator is a one-shot iterator; converting it to a list consumes it.

### Corrected code

```python
def pair_92(values):
    first = [value * 2 for value in values]
    second = [value * 2 for value in values]
    return first, second
```

### Regression tests

```python
assert pair_92([1, 2]) == ([2, 4], [2, 4])
```


## PY-M-093: frequency overwrite

- Difficulty: Medium
- Perspective: Dictionary invariants
- Concept: frequency overwrite
- Symptom: The frequency is always one.
- Diagnostic goal: Identify the update that must use the previous count.

### Buggy code

```python
def frequencies_93(values):
    counts = {}
    for value in values:
        counts[value] = 1
    return counts
```

### Expected diagnosis

Each occurrence overwrites the previous count instead of incrementing it.

### Corrected code

```python
def frequencies_93(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
```

### Regression tests

```python
assert frequencies_93(['a', 'b', 'a']) == {'a': 2, 'b': 1}
```


## PY-M-094: missing base case

- Difficulty: Medium
- Perspective: Recursion tracing
- Concept: missing base case
- Symptom: The call stack grows until RecursionError.
- Diagnostic goal: Find the smallest valid input and prove progress toward it.

### Buggy code

```python
def countdown_94(value):
    print(value)
    return countdown_94(value - 1)
```

### Expected diagnosis

The function never stops at its base case, so recursive calls continue past zero.

### Corrected code

```python
def countdown_94(value):
    if value <= 0:
        return []
    return [value] + countdown_94(value - 1)
```

### Regression tests

```python
assert countdown_94(3) == [3, 2, 1]
assert countdown_94(0) == []
```


## PY-M-095: incorrect insertion boundary

- Difficulty: Medium
- Perspective: Sorting invariant
- Concept: incorrect insertion boundary
- Symptom: The output is not sorted when equal values occur.
- Diagnostic goal: State the invariant before and after inserting one item.

### Buggy code

```python
def insertion_95(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] < value:
            index += 1
        result.insert(index, value)
    return result
```

### Expected diagnosis

The loop inserts before equal elements and therefore reverses their order; use <= for a stable insertion policy.

### Corrected code

```python
def insertion_95(values):
    result = []
    for value in values:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result
```

### Regression tests

```python
assert insertion_95([3, 1, 2]) == [1, 2, 3]
```


## PY-M-096: resource leak

- Difficulty: Medium
- Perspective: Context management
- Concept: resource leak
- Symptom: An opened file remains unclosed on an exception.
- Diagnostic goal: Locate the path that bypasses cleanup.

### Buggy code

```python
def first_line_96(path):
    handle = open(path)
    line = handle.readline()
    if not line:
        raise ValueError('empty')
    handle.close()
    return line.strip()
```

### Expected diagnosis

The exception path skips handle.close; a context manager closes the resource on every exit path.

### Corrected code

```python
def first_line_96(path):
    with open(path) as handle:
        line = handle.readline()
    if not line:
        raise ValueError('empty')
    return line.strip()
```

### Regression tests

```python
# Regression: verify an empty file raises without leaving an open handle.
# Verify a one-line file returns its stripped line.
```


## PY-M-097: partial validation

- Difficulty: Medium
- Perspective: Validation contract
- Concept: partial validation
- Symptom: Malformed records reach arithmetic code and raise later.
- Diagnostic goal: Validate shape and value before using the record.

### Buggy code

```python
def total_price_97(records):
    return sum(record['price'] for record in records)
```

### Expected diagnosis

The function assumes every record has a numeric price; the contract should reject malformed input at the boundary.

### Corrected code

```python
def total_price_97(records):
    total = 0
    for record in records:
        price = record.get('price')
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError('price must be a non-negative number')
        total += price
    return total
```

### Regression tests

```python
assert total_price_97([{'price': 2}, {'price': 3}]) == 5
# Regression: missing, negative and boolean prices must raise ValueError.
```


## PY-M-098: repeated linear lookup

- Difficulty: Medium
- Perspective: Complexity reasoning
- Concept: repeated linear lookup
- Symptom: The function becomes slow as the input grows.
- Diagnostic goal: Identify the repeated work inside the loop.

### Buggy code

```python
def common_98(left, right):
    return [value for value in left if value in right]
```

### Expected diagnosis

Membership in a list scans the right-hand list for every left-hand value, producing quadratic behavior.

### Corrected code

```python
def common_98(left, right):
    available = set(right)
    return [value for value in left if value in available]
```

### Regression tests

```python
assert common_98([1, 2, 2], [2, 3]) == [2, 2]
# Regression: benchmark disjoint lists of 10_000 items.
```


## PY-M-099: late binding closure

- Difficulty: Medium
- Perspective: Closure/state
- Concept: late binding closure
- Symptom: Every callback reports the final loop value.
- Diagnostic goal: Trace when the callback reads the captured variable.

### Buggy code

```python
def callbacks_99(values):
    return [lambda: value for value in values]
```

### Expected diagnosis

Closures capture the variable, not its current value; all callbacks read the final binding later.

### Corrected code

```python
def callbacks_99(values):
    return [lambda value=value: value for value in values]
```

### Regression tests

```python
functions = callbacks_99([1, 2, 3])
assert [function() for function in functions] == [1, 2, 3]
```


## PY-M-100: shallow copy

- Difficulty: Medium
- Perspective: Aliasing analysis
- Concept: shallow copy
- Symptom: Changing one nested record changes another.
- Diagnostic goal: Trace which objects are shared.

### Buggy code

```python
def clone_100(profile):
    copy = profile.copy()
    copy['settings']['dark'] = True
    return profile, copy
```

### Expected diagnosis

dict.copy duplicates only the outer dictionary; the nested settings dictionary remains shared.

### Corrected code

```python
from copy import deepcopy

def clone_100(profile):
    copy = deepcopy(profile)
    copy['settings']['dark'] = True
    return profile, copy
```

### Regression tests

```python
original, changed = clone_100({'settings': {'dark': False}})
assert original['settings']['dark'] is False
```


## PY-H-001: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_1(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_1(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-002: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account2:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account2:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account2(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-003: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_3(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_3(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-004: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key4:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key4) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key4:
    value: str
```

### Regression tests

```python
key = Key4('a')
values = {key: 1}
assert values[Key4('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-005: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_5(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_5(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_5({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-006: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_6 = {}

def total_6(values):
    key = id(values)
    if key not in cache_6: cache_6[key] = sum(values)
    return cache_6[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_6(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-007: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_7(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_7(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_7('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-008: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_8(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_8(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_8(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-009: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_9(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_9(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_9([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-010: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_10(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_10(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-011: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account11:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account11:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account11(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-012: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_12(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_12(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-013: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key13:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key13) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key13:
    value: str
```

### Regression tests

```python
key = Key13('a')
values = {key: 1}
assert values[Key13('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-014: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_14(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_14(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_14({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-015: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_15 = {}

def total_15(values):
    key = id(values)
    if key not in cache_15: cache_15[key] = sum(values)
    return cache_15[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_15(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-016: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_16(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_16(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_16('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-017: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_17(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_17(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_17(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-018: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_18(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_18(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_18([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-019: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_19(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_19(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-020: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account20:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account20:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account20(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-021: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_21(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_21(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-022: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key22:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key22) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key22:
    value: str
```

### Regression tests

```python
key = Key22('a')
values = {key: 1}
assert values[Key22('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-023: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_23(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_23(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_23({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-024: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_24 = {}

def total_24(values):
    key = id(values)
    if key not in cache_24: cache_24[key] = sum(values)
    return cache_24[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_24(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-025: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_25(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_25(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_25('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-026: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_26(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_26(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_26(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-027: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_27(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_27(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_27([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-028: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_28(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_28(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-029: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account29:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account29:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account29(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-030: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_30(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_30(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-031: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key31:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key31) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key31:
    value: str
```

### Regression tests

```python
key = Key31('a')
values = {key: 1}
assert values[Key31('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-032: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_32(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_32(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_32({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-033: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_33 = {}

def total_33(values):
    key = id(values)
    if key not in cache_33: cache_33[key] = sum(values)
    return cache_33[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_33(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-034: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_34(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_34(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_34('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-035: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_35(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_35(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_35(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-036: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_36(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_36(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_36([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-037: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_37(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_37(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-038: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account38:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account38:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account38(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-039: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_39(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_39(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-040: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key40:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key40) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key40:
    value: str
```

### Regression tests

```python
key = Key40('a')
values = {key: 1}
assert values[Key40('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-041: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_41(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_41(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_41({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-042: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_42 = {}

def total_42(values):
    key = id(values)
    if key not in cache_42: cache_42[key] = sum(values)
    return cache_42[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_42(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-043: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_43(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_43(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_43('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-044: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_44(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_44(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_44(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-045: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_45(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_45(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_45([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-046: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_46(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_46(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-047: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account47:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account47:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account47(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-048: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_48(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_48(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-049: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key49:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key49) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key49:
    value: str
```

### Regression tests

```python
key = Key49('a')
values = {key: 1}
assert values[Key49('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-050: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_50(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_50(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_50({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-051: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_51 = {}

def total_51(values):
    key = id(values)
    if key not in cache_51: cache_51[key] = sum(values)
    return cache_51[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_51(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-052: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_52(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_52(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_52('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-053: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_53(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_53(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_53(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-054: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_54(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_54(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_54([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-055: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_55(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_55(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-056: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account56:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account56:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account56(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-057: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_57(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_57(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-058: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key58:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key58) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key58:
    value: str
```

### Regression tests

```python
key = Key58('a')
values = {key: 1}
assert values[Key58('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-059: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_59(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_59(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_59({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-060: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_60 = {}

def total_60(values):
    key = id(values)
    if key not in cache_60: cache_60[key] = sum(values)
    return cache_60[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_60(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-061: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_61(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_61(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_61('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-062: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_62(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_62(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_62(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-063: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_63(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_63(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_63([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-064: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_64(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_64(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-065: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account65:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account65:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account65(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-066: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_66(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_66(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-067: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key67:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key67) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key67:
    value: str
```

### Regression tests

```python
key = Key67('a')
values = {key: 1}
assert values[Key67('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-068: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_68(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_68(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_68({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-069: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_69 = {}

def total_69(values):
    key = id(values)
    if key not in cache_69: cache_69[key] = sum(values)
    return cache_69[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_69(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-070: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_70(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_70(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_70('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-071: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_71(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_71(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_71(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-072: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_72(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_72(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_72([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-073: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_73(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_73(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-074: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account74:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account74:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account74(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-075: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_75(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_75(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-076: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key76:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key76) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key76:
    value: str
```

### Regression tests

```python
key = Key76('a')
values = {key: 1}
assert values[Key76('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-077: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_77(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_77(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_77({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-078: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_78 = {}

def total_78(values):
    key = id(values)
    if key not in cache_78: cache_78[key] = sum(values)
    return cache_78[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_78(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-079: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_79(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_79(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_79('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-080: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_80(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_80(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_80(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-081: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_81(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_81(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_81([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-082: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_82(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_82(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-083: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account83:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account83:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account83(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-084: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_84(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_84(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-085: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key85:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key85) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key85:
    value: str
```

### Regression tests

```python
key = Key85('a')
values = {key: 1}
assert values[Key85('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-086: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_86(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_86(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_86({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-087: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_87 = {}

def total_87(values):
    key = id(values)
    if key not in cache_87: cache_87[key] = sum(values)
    return cache_87[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_87(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-088: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_88(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_88(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_88('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-089: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_89(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_89(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_89(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-090: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_90(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_90(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_90([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-091: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_91(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_91(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```


## PY-H-092: incorrect property setter

- Difficulty: Hard
- Perspective: Descriptor/protocol reasoning
- Concept: incorrect property setter
- Symptom: Assignment silently writes the wrong attribute.
- Diagnostic goal: Follow descriptor calls and storage names.

### Buggy code

```python
class Account92:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self.balance = value
```

### Expected diagnosis

The setter assigns to the property again, recursively invoking itself until RecursionError.

### Corrected code

```python
class Account92:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError('balance cannot be negative')
        self._balance = value
```

### Regression tests

```python
account = Account92(10)
account.balance = 20
assert account.balance == 20
# Regression: negative assignment raises ValueError.
```


## PY-H-093: blocking event loop

- Difficulty: Hard
- Perspective: Async reasoning
- Concept: blocking event loop
- Symptom: Independent async tasks run serially.
- Diagnostic goal: Distinguish blocking work from awaitable work.

### Buggy code

```python
import asyncio
import time

async def task_93(delay):
    time.sleep(delay)
    return delay
```

### Expected diagnosis

time.sleep blocks the event-loop thread. An async task must yield with asyncio.sleep or move blocking work to an executor.

### Corrected code

```python
import asyncio

async def task_93(delay):
    await asyncio.sleep(delay)
    return delay
```

### Regression tests

```python
# Regression: gather two tasks and assert elapsed time is close to the longest delay, not their sum.
```


## PY-H-094: hashable mutable key

- Difficulty: Hard
- Perspective: Data model invariants
- Concept: hashable mutable key
- Symptom: A dictionary lookup fails after a key object changes.
- Diagnostic goal: Explain why equality and hashing must remain stable.

### Buggy code

```python
class Key94:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return isinstance(other, Key94) and self.value == other.value
```

### Expected diagnosis

A mutable field participates in hashing, so changing it after insertion moves the logical key without reindexing the dictionary.

### Corrected code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Key94:
    value: str
```

### Regression tests

```python
key = Key94('a')
values = {key: 1}
assert values[Key94('a')] == 1
# Regression: keys must be immutable after insertion.
```


## PY-H-095: graph visited too late

- Difficulty: Hard
- Perspective: Algorithm invariant
- Concept: graph visited too late
- Symptom: A cyclic graph causes repeated work or recursion failure.
- Diagnostic goal: State exactly when a node becomes visited.

### Buggy code

```python
def walk_95(graph, start):
    seen = set()
    order = []
    def visit(node):
        for neighbor in graph.get(node, []):
            visit(neighbor)
        seen.add(node)
        order.append(node)
    visit(start)
    return order
```

### Expected diagnosis

The node is marked only after exploring children, so a cycle can re-enter it indefinitely.

### Corrected code

```python
def walk_95(graph, start):
    seen = set()
    order = []
    def visit(node):
        if node in seen:
            return
        seen.add(node)
        order.append(node)
        for neighbor in graph.get(node, []):
            visit(neighbor)
    visit(start)
    return order
```

### Regression tests

```python
assert set(walk_95({'a': ['b'], 'b': ['a']}, 'a')) == {'a', 'b'}
```


## PY-H-096: stale memoization

- Difficulty: Hard
- Perspective: Caching correctness
- Concept: stale memoization
- Symptom: A cached answer reflects an earlier mutable input.
- Diagnostic goal: Check whether the cache key captures all relevant state.

### Buggy code

```python
cache_96 = {}

def total_96(values):
    key = id(values)
    if key not in cache_96: cache_96[key] = sum(values)
    return cache_96[key]
```

### Expected diagnosis

The object identity remains the same after mutation, but the value used by the computation changes.

### Corrected code

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def total_96(values):
    return sum(values)
```

### Regression tests

```python
# Regression: call with a tuple, then a different tuple; mutable lists must be converted before caching.
```


## PY-H-097: unsafe evaluation

- Difficulty: Hard
- Perspective: Parsing/security boundary
- Concept: unsafe evaluation
- Symptom: Input can execute arbitrary code.
- Diagnostic goal: Separate parsing data from executing expressions.

### Buggy code

```python
def calculate_97(text):
    return eval(text)
```

### Expected diagnosis

eval treats untrusted input as Python code and can access dangerous operations.

### Corrected code

```python
import ast

def calculate_97(text):
    tree = ast.parse(text, mode='eval')
    if not all(isinstance(node, (ast.Expression, ast.Constant, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div)) for node in ast.walk(tree)):
        raise ValueError('unsupported expression')
    return eval(compile(tree, '<expression>', 'eval'), {'__builtins__': {}}, {})
```

### Regression tests

```python
assert calculate_97('2 + 3') == 5
# Regression: reject '__import__(...)' and attribute access.
```


## PY-H-098: partial mutation on failure

- Difficulty: Hard
- Perspective: Transactional reasoning
- Concept: partial mutation on failure
- Symptom: A failed update leaves half the state changed.
- Diagnostic goal: Identify the commit point and make the operation atomic.

### Buggy code

```python
def transfer_98(accounts, source, target, amount):
    accounts[source] -= amount
    if accounts[source] < 0:
        raise ValueError('insufficient funds')
    accounts[target] += amount
```

### Expected diagnosis

The source balance is modified before validation completes; an exception leaves the state corrupted.

### Corrected code

```python
def transfer_98(accounts, source, target, amount):
    if amount < 0 or accounts[source] < amount:
        raise ValueError('invalid transfer')
    updated = accounts.copy()
    updated[source] -= amount
    updated[target] += amount
    accounts.update(updated)
```

### Regression tests

```python
accounts = {'a': 5, 'b': 1}
try: transfer_98(accounts, 'a', 'b', 10)
except ValueError: pass
assert accounts == {'a': 5, 'b': 1}
```


## PY-H-099: quadratic duplicate removal

- Difficulty: Hard
- Perspective: Complexity and correctness
- Concept: quadratic duplicate removal
- Symptom: The output is correct but does not scale.
- Diagnostic goal: Preserve order while maintaining linear expected work.

### Buggy code

```python
def unique_99(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
```

### Expected diagnosis

Searching the growing result list for every value is quadratic. A set records membership independently of output order.

### Corrected code

```python
def unique_99(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
```

### Regression tests

```python
assert unique_99([3, 1, 3, 2, 1]) == [3, 1, 2]
# Regression: benchmark 100_000 repeated values.
```


## PY-H-100: shared mutable state

- Difficulty: Hard
- Perspective: Concurrency reasoning
- Concept: shared mutable state
- Symptom: Concurrent updates lose increments.
- Diagnostic goal: Identify the invariant violated by the interleaving.

### Buggy code

```python
def increment_100(state, times):
    for _ in range(times):
        state['count'] = state['count'] + 1
```

### Expected diagnosis

The read-modify-write sequence is not atomic when shared across threads; updates can overwrite one another.

### Corrected code

```python
from threading import Lock

def increment_100(state, times, lock):
    for _ in range(times):
        with lock:
            state['count'] += 1
```

### Regression tests

```python
# Regression: run two workers repeatedly and assert count equals both contributions.
```

