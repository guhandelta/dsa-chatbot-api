# Ruby Debug Exercises

A RAG-training corpus of 300 debugging exercises for Ruby. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, state, memory/ownership, concurrency, errors, APIs, security, persistence, and testing

## RUBY-E-001: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-002: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-003: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-004: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-005: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-006: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-007: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-008: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-009: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-010: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-011: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-012: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-013: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-014: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-015: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-016: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-017: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-018: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-019: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-020: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-021: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-022: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-023: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-024: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-025: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-026: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-027: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-028: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-029: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-030: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-031: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-032: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-033: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-034: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-035: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-036: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-037: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-038: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-039: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-040: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-041: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-042: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-043: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-044: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-045: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-046: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-047: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-048: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-049: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-050: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-051: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-052: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-053: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-054: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-055: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-056: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-057: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-058: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-059: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-060: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-061: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-062: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-063: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-064: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-065: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-066: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-067: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-068: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-069: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-070: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-071: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-072: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-073: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-074: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-075: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-076: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-077: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-078: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-079: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-080: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-081: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-082: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-083: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-084: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-085: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-086: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-087: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-088: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-089: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-090: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-E-091: block variable leakage

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-E-092: nil versus false

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-E-093: mutating during each

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-E-094: rescue too broad

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-E-095: mutable default state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-E-096: identity versus value equality

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-E-097: shared mutable state

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-E-098: file not closed

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-E-099: method_missing hides typos

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-E-100: unsafe eval

- Difficulty: Easy
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-001: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-002: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-003: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-004: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-005: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-006: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-007: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-008: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-009: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-010: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-011: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-012: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-013: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-014: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-015: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-016: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-017: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-018: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-019: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-020: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-021: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-022: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-023: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-024: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-025: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-026: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-027: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-028: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-029: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-030: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-031: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-032: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-033: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-034: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-035: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-036: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-037: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-038: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-039: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-040: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-041: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-042: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-043: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-044: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-045: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-046: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-047: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-048: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-049: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-050: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-051: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-052: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-053: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-054: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-055: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-056: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-057: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-058: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-059: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-060: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-061: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-062: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-063: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-064: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-065: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-066: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-067: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-068: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-069: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-070: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-071: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-072: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-073: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-074: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-075: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-076: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-077: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-078: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-079: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-080: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-081: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-082: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-083: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-084: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-085: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-086: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-087: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-088: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-089: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-090: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-M-091: block variable leakage

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-M-092: nil versus false

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-M-093: mutating during each

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-M-094: rescue too broad

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-M-095: mutable default state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-M-096: identity versus value equality

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-M-097: shared mutable state

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-M-098: file not closed

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-M-099: method_missing hides typos

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-M-100: unsafe eval

- Difficulty: Medium
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-001: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-002: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-003: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-004: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-005: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-006: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-007: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-008: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-009: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-010: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-011: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-012: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-013: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-014: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-015: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-016: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-017: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-018: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-019: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-020: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-021: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-022: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-023: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-024: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-025: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-026: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-027: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-028: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-029: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-030: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-031: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-032: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-033: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-034: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-035: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-036: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-037: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-038: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-039: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-040: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-041: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-042: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-043: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-044: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-045: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-046: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-047: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-048: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-049: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-050: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-051: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-052: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-053: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-054: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-055: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-056: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-057: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-058: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-059: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-060: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-061: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-062: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-063: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-064: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-065: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-066: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-067: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-068: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-069: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-070: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-071: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-072: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-073: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-074: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-075: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-076: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-077: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-078: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-079: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-080: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-081: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-082: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-083: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-084: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-085: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-086: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-087: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-088: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-089: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-090: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```

## RUBY-H-091: block variable leakage

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Blocks
- Concept: block variable leakage
- Symptom: A later expression sees an unexpected value.
- Diagnostic goal: Keep block-local state explicit.

### Buggy code

```ruby
values = [1, 2]
values.each { |value| total = value }
puts total
```

### Expected diagnosis

The assignment creates or changes outer state; the loop does not accumulate a meaningful result.

### Corrected code

```ruby
total = values.sum
```

### Regression tests

```ruby
raise unless total == 3
```

## RUBY-H-092: nil versus false

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Object model
- Concept: nil versus false
- Symptom: A guard accepts an invalid value.
- Diagnostic goal: Remember that only nil and false are falsey in Ruby.

### Buggy code

```ruby
return fallback unless value
```

### Expected diagnosis

Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.

### Corrected code

```ruby
return fallback if value.nil? || value == false
```

### Regression tests

```ruby
raise unless enabled?(0) == expected
```

## RUBY-H-093: mutating during each

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Collections
- Concept: mutating during each
- Symptom: Elements are skipped after deletion.
- Diagnostic goal: Use select/reject or iterate over a copy.

### Buggy code

```ruby
items.each { |item| items.delete(item) if item.expired? }
```

### Expected diagnosis

Deleting while iterating changes indexes and can skip adjacent values.

### Corrected code

```ruby
items = items.reject(&:expired?)
```

### Regression tests

```ruby
raise unless clean(items).none?(&:expired?)
```

## RUBY-H-094: rescue too broad

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Exceptions
- Concept: rescue too broad
- Symptom: Programming errors become normal results.
- Diagnostic goal: Rescue only expected exception classes.

### Buggy code

```ruby
begin
  parse(input)
rescue
  nil
end
```

### Expected diagnosis

A bare rescue catches StandardError broadly and hides defects.

### Corrected code

```ruby
begin
  parse(input)
rescue ArgumentError
  nil
end
```

### Regression tests

```ruby
raise unless malformed_returns_nil
```

## RUBY-H-095: mutable default state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Contracts
- Concept: mutable default state
- Symptom: Calls share state unexpectedly.
- Diagnostic goal: Create mutable defaults per call.

### Buggy code

```ruby
def add(value, bucket = [])
  bucket << value
end
```

### Expected diagnosis

Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.

### Corrected code

```ruby
def add(value, bucket: nil)
  bucket = [] if bucket.nil?
  bucket << value
end
```

### Regression tests

```ruby
raise unless add(:a) == [:a] && add(:b) == [:b]
```

## RUBY-H-096: identity versus value equality

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Equality
- Concept: identity versus value equality
- Symptom: Equivalent records do not compare equal.
- Diagnostic goal: Choose ==/eql? and hash consistently.

### Buggy code

```ruby
a = User.new(1)
b = User.new(1)
raise unless a.equal?(b)
```

### Expected diagnosis

equal? tests object identity, not domain value equality.

### Corrected code

```ruby
raise unless a == b
```

### Regression tests

```ruby
raise unless User.new(1) == User.new(1)
```

## RUBY-H-097: shared mutable state

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Concurrency
- Concept: shared mutable state
- Symptom: Threaded increments lose updates.
- Diagnostic goal: Protect the read-modify-write operation.

### Buggy code

```ruby
count += 1
```

### Expected diagnosis

A compound update is not a synchronization contract even when individual operations appear simple.

### Corrected code

```ruby
mutex.synchronize { count += 1 }
```

### Regression tests

```ruby
raise unless concurrent_count == expected
```

## RUBY-H-098: file not closed

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Resources
- Concept: file not closed
- Symptom: Descriptors remain open on an error path.
- Diagnostic goal: Use the block form of resource APIs.

### Buggy code

```ruby
file = File.open(path)
process(file)
file.close
```

### Expected diagnosis

An exception from process skips close.

### Corrected code

```ruby
File.open(path) { |file| process(file) }
```

### Regression tests

```ruby
raise unless closed_after_success_and_failure
```

## RUBY-H-099: method_missing hides typos

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Metaprogramming
- Concept: method_missing hides typos
- Symptom: A misspelled method returns a plausible value.
- Diagnostic goal: Use explicit interfaces and narrow dynamic dispatch.

### Buggy code

```ruby
def method_missing(name, *args)
  nil
end
```

### Expected diagnosis

Swallowing every unknown method turns programmer errors into silent data errors.

### Corrected code

```ruby
def method_missing(name, *args)
  super
end
```

### Regression tests

```ruby
raise NoMethodError unless missing_method_raises
```

## RUBY-H-100: unsafe eval

- Difficulty: Hard
- Language/framework: Ruby / Ruby
- Perspective: Parsing
- Concept: unsafe eval
- Symptom: Input executes arbitrary Ruby code.
- Diagnostic goal: Parse data rather than evaluating source.

### Buggy code

```ruby
eval(params[:expression])
```

### Expected diagnosis

eval executes attacker-controlled code in the process.

### Corrected code

```ruby
JSON.parse(params[:payload])
```

### Regression tests

```ruby
raise unless malicious_expression_is_rejected
```
