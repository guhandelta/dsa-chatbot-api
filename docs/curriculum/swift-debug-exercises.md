# Swift Debug Exercises

A RAG-training corpus of 300 debugging exercises for Swift. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, memory, state, concurrency, errors, collections, APIs, testing, and performance

## SWIFT-E-001: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-002: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-003: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-004: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-005: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-006: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-007: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-008: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-009: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-010: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-011: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-012: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-013: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-014: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-015: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-016: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-017: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-018: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-019: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-020: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-021: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-022: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-023: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-024: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-025: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-026: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-027: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-028: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-029: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-030: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-031: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-032: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-033: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-034: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-035: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-036: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-037: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-038: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-039: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-040: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-041: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-042: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-043: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-044: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-045: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-046: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-047: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-048: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-049: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-050: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-051: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-052: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-053: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-054: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-055: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-056: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-057: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-058: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-059: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-060: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-061: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-062: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-063: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-064: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-065: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-066: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-067: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-068: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-069: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-070: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-071: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-072: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-073: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-074: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-075: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-076: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-077: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-078: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-079: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-080: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-081: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-082: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-083: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-084: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-085: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-086: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-087: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-088: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-089: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-090: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-E-091: forced unwrap

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-E-092: mutating copy

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-E-093: actor isolation

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-E-094: retain cycle

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-E-095: try! at boundary

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-E-096: mutating while iterating

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-E-097: existential mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-E-098: task lifetime

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-E-099: date format mismatch

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-E-100: copy in hot loop

- Difficulty: Easy
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-001: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-002: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-003: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-004: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-005: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-006: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-007: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-008: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-009: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-010: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-011: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-012: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-013: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-014: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-015: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-016: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-017: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-018: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-019: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-020: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-021: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-022: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-023: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-024: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-025: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-026: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-027: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-028: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-029: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-030: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-031: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-032: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-033: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-034: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-035: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-036: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-037: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-038: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-039: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-040: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-041: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-042: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-043: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-044: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-045: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-046: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-047: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-048: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-049: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-050: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-051: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-052: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-053: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-054: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-055: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-056: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-057: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-058: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-059: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-060: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-061: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-062: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-063: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-064: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-065: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-066: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-067: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-068: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-069: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-070: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-071: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-072: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-073: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-074: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-075: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-076: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-077: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-078: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-079: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-080: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-081: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-082: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-083: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-084: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-085: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-086: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-087: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-088: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-089: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-090: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-M-091: forced unwrap

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-M-092: mutating copy

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-M-093: actor isolation

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-M-094: retain cycle

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-M-095: try! at boundary

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-M-096: mutating while iterating

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-M-097: existential mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-M-098: task lifetime

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-M-099: date format mismatch

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-M-100: copy in hot loop

- Difficulty: Medium
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-001: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-002: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-003: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-004: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-005: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-006: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-007: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-008: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-009: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-010: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-011: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-012: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-013: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-014: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-015: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-016: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-017: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-018: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-019: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-020: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-021: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-022: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-023: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-024: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-025: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-026: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-027: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-028: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-029: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-030: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-031: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-032: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-033: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-034: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-035: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-036: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-037: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-038: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-039: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-040: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-041: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-042: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-043: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-044: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-045: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-046: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-047: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-048: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-049: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-050: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-051: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-052: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-053: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-054: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-055: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-056: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-057: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-058: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-059: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-060: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-061: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-062: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-063: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-064: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-065: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-066: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-067: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-068: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-069: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-070: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-071: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-072: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-073: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-074: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-075: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-076: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-077: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-078: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-079: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-080: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-081: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-082: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-083: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-084: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-085: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-086: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-087: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-088: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-089: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-090: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```

## SWIFT-H-091: forced unwrap

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Optionals
- Concept: forced unwrap
- Symptom: A missing API value crashes the app.
- Diagnostic goal: Bind or provide a deliberate fallback.

### Buggy code

```swift
let name = user.profile!.name
```

### Expected diagnosis

The force unwrap converts an expected absence into a runtime trap.

### Corrected code

```swift
guard let profile = user.profile else { return .guest }
let name = profile.name
```

### Regression tests

```swift
XCTAssertEqual(display(userWithoutProfile), "guest")
```

## SWIFT-H-092: mutating copy

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Value semantics
- Concept: mutating copy
- Symptom: A change to a struct does not update the original.
- Diagnostic goal: Understand copy-on-write and return the updated value.

### Buggy code

```swift
func add(_ item: Item, to list: [Item]) { var list = list; list.append(item) }
```

### Expected diagnosis

The parameter is a local value copy; its mutation is not visible to the caller.

### Corrected code

```swift
func adding(_ item: Item, to list: [Item]) -> [Item] { list + [item] }
```

### Regression tests

```swift
XCTAssertEqual(adding(item, to: []), [item])
```

## SWIFT-H-093: actor isolation

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Concurrency
- Concept: actor isolation
- Symptom: A property is accessed from the wrong isolation domain.
- Diagnostic goal: Await actor state or expose a safe method.

### Buggy code

```swift
Task { print(counter.value) }
```

### Expected diagnosis

Actor-isolated state cannot be synchronously accessed from an arbitrary task.

### Corrected code

```swift
Task { print(await counter.value) }
```

### Regression tests

```swift
awaitAssertCounterRead()
```

## SWIFT-H-094: retain cycle

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: ARC
- Concept: retain cycle
- Symptom: A controller never deallocates.
- Diagnostic goal: Use weak/unowned references for non-owning closures.

### Buggy code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { self.finish() } } }
```

### Expected diagnosis

The closure strongly captures self while self retains the closure.

### Corrected code

```swift
class Controller { var onDone: (() -> Void)?
  func bind() { onDone = { [weak self] in self?.finish() } } }
```

### Regression tests

```swift
assertDeinitAfterControllerRelease()
```

## SWIFT-H-095: try! at boundary

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Errors
- Concept: try! at boundary
- Symptom: Malformed data crashes instead of returning an error.
- Diagnostic goal: Propagate throws or map the error to a user-facing result.

### Buggy code

```swift
let value = try! decoder.decode(Model.self, from: data)
```

### Expected diagnosis

try! traps when decoding fails.

### Corrected code

```swift
let value = try decoder.decode(Model.self, from: data)
```

### Regression tests

```swift
XCTAssertThrowsError(try decode(invalidData))
```

## SWIFT-H-096: mutating while iterating

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Collections
- Concept: mutating while iterating
- Symptom: The loop skips or traps after removal.
- Diagnostic goal: Use filter or collect indexes before mutation.

### Buggy code

```swift
for item in items { if item.expired { items.removeAll { $0.id == item.id } } }
```

### Expected diagnosis

Changing a collection during iteration invalidates the traversal.

### Corrected code

```swift
items.removeAll { $0.expired }
```

### Regression tests

```swift
XCTAssertEqual(items.filter { !$0.expired }, expected)
```

## SWIFT-H-097: existential mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Protocols
- Concept: existential mismatch
- Symptom: A generic function cannot accept the protocol value.
- Diagnostic goal: Preserve associated-type constraints or erase deliberately.

### Buggy code

```swift
func merge<T: Sequence>(_ a: T, _ b: T) -> T { ... }
```

### Expected diagnosis

Two sequences with associated types are not necessarily constructible as the same concrete T.

### Corrected code

```swift
func merge<S: Sequence>(_ a: S, _ b: S) -> [S.Element] { Array(a) + Array(b) }
```

### Regression tests

```swift
XCTAssertEqual(merge([1], [2]), [1,2])
```

## SWIFT-H-098: task lifetime

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Async
- Concept: task lifetime
- Symptom: A detached task outlives the owner and updates stale UI.
- Diagnostic goal: Tie task cancellation to the owner lifecycle.

### Buggy code

```swift
Task.detached { await updateView() }
```

### Expected diagnosis

Detached work ignores actor context and cancellation ownership.

### Corrected code

```swift
let task = Task { await updateView() }
// cancel task in deinit or view disappearance
```

### Regression tests

```swift
assertTaskCancelledOnDisappear()
```

## SWIFT-H-099: date format mismatch

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Persistence
- Concept: date format mismatch
- Symptom: Decoded records fail only for some locales.
- Diagnostic goal: Use an explicit stable date strategy.

### Buggy code

```swift
JSONDecoder().decode(Event.self, from: data)
```

### Expected diagnosis

Default date decoding is not a contract for arbitrary wire formats.

### Corrected code

```swift
let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
```

### Regression tests

```swift
XCTAssertNoThrow(try decoder.decode(Event.self, from: isoData))
```

## SWIFT-H-100: copy in hot loop

- Difficulty: Hard
- Language/framework: Swift / Swift
- Perspective: Performance
- Concept: copy in hot loop
- Symptom: A large value is repeatedly copied.
- Diagnostic goal: Use inout or a reference only when ownership is intentional.

### Buggy code

```swift
for _ in 0..<n { process(largeStruct) }
```

### Expected diagnosis

Repeated value copies can dominate a hot path.

### Corrected code

```swift
withUnsafeMutablePointer(to: &largeStruct) { process($0.pointee) }
```

### Regression tests

```swift
measureCopyCostAndAssertBudget()
```
