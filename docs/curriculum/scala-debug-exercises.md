# Scala Debug Exercises

A RAG-training corpus of 300 debugging exercises for Scala. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, memory, state, concurrency, errors, collections, APIs, testing, and performance

## SCALA-E-001: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-002: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-003: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-004: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-005: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-006: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-007: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-008: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-009: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-010: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-011: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-012: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-013: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-014: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-015: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-016: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-017: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-018: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-019: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-020: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-021: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-022: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-023: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-024: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-025: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-026: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-027: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-028: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-029: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-030: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-031: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-032: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-033: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-034: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-035: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-036: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-037: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-038: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-039: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-040: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-041: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-042: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-043: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-044: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-045: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-046: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-047: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-048: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-049: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-050: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-051: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-052: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-053: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-054: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-055: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-056: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-057: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-058: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-059: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-060: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-061: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-062: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-063: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-064: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-065: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-066: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-067: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-068: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-069: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-070: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-071: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-072: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-073: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-074: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-075: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-076: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-077: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-078: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-079: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-080: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-081: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-082: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-083: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-084: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-085: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-086: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-087: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-088: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-089: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-090: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-E-091: get on None

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-E-092: map versus flatMap

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-E-093: Option(null)

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-E-094: wrong implicit

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-E-095: blocking Await

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-E-096: shared mutable state

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-E-097: non-exhaustive match

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-E-098: Nothing inference

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-E-099: Source not closed

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-E-100: reference equality

- Difficulty: Easy
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-001: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-002: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-003: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-004: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-005: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-006: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-007: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-008: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-009: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-010: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-011: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-012: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-013: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-014: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-015: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-016: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-017: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-018: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-019: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-020: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-021: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-022: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-023: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-024: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-025: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-026: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-027: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-028: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-029: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-030: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-031: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-032: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-033: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-034: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-035: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-036: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-037: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-038: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-039: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-040: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-041: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-042: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-043: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-044: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-045: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-046: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-047: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-048: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-049: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-050: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-051: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-052: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-053: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-054: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-055: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-056: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-057: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-058: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-059: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-060: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-061: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-062: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-063: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-064: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-065: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-066: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-067: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-068: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-069: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-070: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-071: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-072: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-073: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-074: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-075: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-076: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-077: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-078: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-079: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-080: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-081: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-082: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-083: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-084: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-085: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-086: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-087: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-088: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-089: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-090: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-M-091: get on None

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-M-092: map versus flatMap

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-M-093: Option(null)

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-M-094: wrong implicit

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-M-095: blocking Await

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-M-096: shared mutable state

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-M-097: non-exhaustive match

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-M-098: Nothing inference

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-M-099: Source not closed

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-M-100: reference equality

- Difficulty: Medium
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-001: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-002: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-003: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-004: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-005: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-006: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-007: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-008: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-009: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-010: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-011: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-012: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-013: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-014: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-015: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-016: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-017: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-018: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-019: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-020: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-021: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-022: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-023: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-024: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-025: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-026: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-027: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-028: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-029: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-030: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-031: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-032: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-033: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-034: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-035: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-036: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-037: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-038: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-039: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-040: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-041: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-042: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-043: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-044: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-045: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-046: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-047: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-048: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-049: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-050: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-051: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-052: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-053: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-054: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-055: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-056: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-057: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-058: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-059: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-060: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-061: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-062: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-063: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-064: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-065: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-066: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-067: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-068: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-069: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-070: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-071: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-072: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-073: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-074: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-075: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-076: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-077: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-078: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-079: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-080: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-081: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-082: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-083: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-084: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-085: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-086: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-087: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-088: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-089: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-090: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```

## SCALA-H-091: get on None

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: get on None
- Symptom: A missing lookup throws NoSuchElementException.
- Diagnostic goal: Keep absence in the Option pipeline.

### Buggy code

```scala
val name = users.get(id).get.name
```

### Expected diagnosis

get is unsafe for an expected missing value.

### Corrected code

```scala
val name = users.get(id).map(_.name).getOrElse("unknown")
```

### Regression tests

```scala
assert(name(unknownId) == "unknown")
```

## SCALA-H-092: map versus flatMap

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Collections
- Concept: map versus flatMap
- Symptom: Nested collections reach the caller.
- Diagnostic goal: Use flatMap when each input produces zero or more outputs.

### Buggy code

```scala
val names = users.map(_.emails.map(_.address))
```

### Expected diagnosis

map preserves the nested structure List[List[String]].

### Corrected code

```scala
val names = users.flatMap(_.emails.map(_.address))
```

### Regression tests

```scala
assert(names == expectedFlatList)
```

## SCALA-H-093: Option(null)

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Options
- Concept: Option(null)
- Symptom: A supposedly present option contains an invalid value.
- Diagnostic goal: Use Option.apply for nullable interop.

### Buggy code

```scala
Some(javaApi.getName)
```

### Expected diagnosis

Some(null) is possible and defeats the absence contract.

### Corrected code

```scala
Option(javaApi.getName)
```

### Regression tests

```scala
assert(Option(null) == None)
```

## SCALA-H-094: wrong implicit

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Implicits
- Concept: wrong implicit
- Symptom: Formatting or ordering changes based on scope.
- Diagnostic goal: Make contextual dependencies explicit or narrowly scoped.

### Buggy code

```scala
implicit val ordering: Ordering[Item] = Ordering.by(_.id)
```

### Expected diagnosis

A broad implicit silently changes unrelated sort behavior.

### Corrected code

```scala
def sortedItems(items: List[Item])(using Ordering[Item]) = items.sorted
```

### Regression tests

```scala
assert(sortedItems(items)(using byName).head == expected)
```

## SCALA-H-095: blocking Await

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Futures
- Concept: blocking Await
- Symptom: A limited execution context starves.
- Diagnostic goal: Compose futures asynchronously and isolate blocking work.

### Buggy code

```scala
Await.result(fetch(), 10.seconds)
```

### Expected diagnosis

Blocking consumes executor threads and can deadlock dependent futures.

### Corrected code

```scala
fetch().map(transform).recover(handle)
```

### Regression tests

```scala
assertFutureCompletesWithoutBlocking())
```

## SCALA-H-096: shared mutable state

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Actors
- Concept: shared mutable state
- Symptom: Concurrent messages corrupt a counter.
- Diagnostic goal: Keep state inside the actor and update through messages.

### Buggy code

```scala
var count = 0
def increment(): Unit = count += 1
```

### Expected diagnosis

External callers can mutate or read state without actor serialization.

### Corrected code

```scala
case object Increment
private var count = 0
case Increment => count += 1
```

### Regression tests

```scala
assertEventually(count == expected)
```

## SCALA-H-097: non-exhaustive match

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Pattern matching
- Concept: non-exhaustive match
- Symptom: A new case causes MatchError.
- Diagnostic goal: Match every sealed hierarchy case or provide a deliberate fallback.

### Buggy code

```scala
status match { case Ready => run() }
```

### Expected diagnosis

The matcher does not handle Failed or Stopped.

### Corrected code

```scala
status match { case Ready => run(); case Failed => recover(); case Stopped => stop() }
```

### Regression tests

```scala
assertAllStatusesHandled())
```

## SCALA-H-098: Nothing inference

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Type inference
- Concept: Nothing inference
- Symptom: A collection is inferred too narrowly.
- Diagnostic goal: Supply a type parameter at empty constructors.

### Buggy code

```scala
val values = List.empty; values :+ 1
```

### Expected diagnosis

List.empty may infer Nothing and constrain later operations.

### Corrected code

```scala
val values: List[Int] = List.empty; values :+ 1
```

### Regression tests

```scala
assert(values == List(1))
```

## SCALA-H-099: Source not closed

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Resources
- Concept: Source not closed
- Symptom: File handles remain open after streaming.
- Diagnostic goal: Close the Source in a managed scope.

### Buggy code

```scala
Source.fromFile(path).getLines().toList
```

### Expected diagnosis

The Source is never closed, especially on exceptions.

### Corrected code

```scala
Using(Source.fromFile(path))(_.getLines().toList)
```

### Regression tests

```scala
assert(readLines(path) == expected)
```

## SCALA-H-100: reference equality

- Difficulty: Hard
- Language/framework: Scala / Scala
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent case class-like Java objects compare unequal.
- Diagnostic goal: Use structural equality or a case class.

### Buggy code

```scala
if (a eq b) true else false
```

### Expected diagnosis

eq tests reference identity, not values.

### Corrected code

```scala
a == b
```

### Regression tests

```scala
assert(Point(1,2) == Point(1,2))
```
