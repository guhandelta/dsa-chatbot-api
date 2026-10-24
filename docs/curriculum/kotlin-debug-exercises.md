# Kotlin Debug Exercises

A RAG-training corpus of 300 debugging exercises for Kotlin. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, memory, state, concurrency, errors, collections, APIs, testing, and performance

## KT-E-001: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-002: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-003: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-004: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-005: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-006: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-007: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-008: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-009: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-010: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-011: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-012: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-013: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-014: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-015: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-016: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-017: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-018: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-019: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-020: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-021: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-022: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-023: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-024: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-025: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-026: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-027: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-028: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-029: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-030: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-031: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-032: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-033: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-034: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-035: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-036: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-037: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-038: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-039: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-040: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-041: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-042: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-043: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-044: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-045: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-046: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-047: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-048: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-049: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-050: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-051: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-052: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-053: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-054: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-055: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-056: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-057: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-058: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-059: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-060: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-061: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-062: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-063: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-064: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-065: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-066: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-067: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-068: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-069: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-070: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-071: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-072: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-073: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-074: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-075: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-076: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-077: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-078: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-079: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-080: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-081: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-082: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-083: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-084: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-085: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-086: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-087: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-088: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-089: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-090: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-E-091: !! at boundary

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-E-092: blocking in suspend function

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-E-093: mutable list exposure

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-E-094: copy shallow state

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-E-095: collect never completes

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-E-096: runCatching hides cancellation

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-E-097: unsafe cast

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-E-098: platform type null

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-E-099: shared mutable fixture

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-E-100: default value masks missing field

- Difficulty: Easy
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-001: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-002: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-003: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-004: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-005: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-006: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-007: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-008: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-009: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-010: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-011: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-012: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-013: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-014: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-015: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-016: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-017: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-018: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-019: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-020: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-021: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-022: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-023: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-024: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-025: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-026: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-027: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-028: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-029: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-030: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-031: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-032: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-033: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-034: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-035: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-036: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-037: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-038: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-039: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-040: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-041: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-042: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-043: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-044: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-045: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-046: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-047: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-048: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-049: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-050: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-051: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-052: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-053: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-054: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-055: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-056: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-057: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-058: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-059: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-060: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-061: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-062: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-063: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-064: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-065: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-066: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-067: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-068: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-069: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-070: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-071: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-072: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-073: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-074: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-075: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-076: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-077: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-078: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-079: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-080: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-081: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-082: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-083: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-084: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-085: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-086: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-087: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-088: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-089: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-090: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-M-091: !! at boundary

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-M-092: blocking in suspend function

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-M-093: mutable list exposure

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-M-094: copy shallow state

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-M-095: collect never completes

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-M-096: runCatching hides cancellation

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-M-097: unsafe cast

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-M-098: platform type null

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-M-099: shared mutable fixture

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-M-100: default value masks missing field

- Difficulty: Medium
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-001: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-002: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-003: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-004: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-005: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-006: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-007: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-008: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-009: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-010: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-011: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-012: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-013: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-014: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-015: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-016: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-017: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-018: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-019: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-020: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-021: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-022: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-023: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-024: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-025: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-026: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-027: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-028: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-029: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-030: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-031: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-032: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-033: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-034: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-035: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-036: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-037: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-038: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-039: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-040: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-041: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-042: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-043: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-044: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-045: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-046: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-047: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-048: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-049: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-050: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-051: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-052: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-053: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-054: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-055: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-056: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-057: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-058: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-059: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-060: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-061: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-062: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-063: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-064: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-065: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-066: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-067: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-068: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-069: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-070: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-071: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-072: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-073: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-074: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-075: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-076: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-077: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-078: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-079: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-080: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-081: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-082: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-083: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-084: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-085: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-086: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-087: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-088: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-089: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-090: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```

## KT-H-091: !! at boundary

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Null safety
- Concept: !! at boundary
- Symptom: A missing value throws KotlinNullPointerException.
- Diagnostic goal: Use safe calls, Elvis, or validated require.

### Buggy code

```kotlin
val name = user.profile!!.name
```

### Expected diagnosis

The non-null assertion bypasses Kotlin’s nullable contract.

### Corrected code

```kotlin
val name = user.profile?.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", display(userWithoutProfile))
```

## KT-H-092: blocking in suspend function

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Coroutines
- Concept: blocking in suspend function
- Symptom: Unrelated coroutines stall.
- Diagnostic goal: Move blocking work to an appropriate dispatcher or use a suspending client.

### Buggy code

```kotlin
suspend fun load() = Files.readString(path)
```

### Expected diagnosis

A blocking file read runs on the caller coroutine thread.

### Corrected code

```kotlin
suspend fun load() = withContext(Dispatchers.IO) { Files.readString(path) }
```

### Regression tests

```kotlin
runTest { assertConcurrentWorkProgresses() }
```

## KT-H-093: mutable list exposure

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Collections
- Concept: mutable list exposure
- Symptom: Callers modify internal state.
- Diagnostic goal: Return an immutable view or defensive copy.

### Buggy code

```kotlin
fun items(): MutableList<Item> = internalItems
```

### Expected diagnosis

The mutable collection leaks ownership.

### Corrected code

```kotlin
fun items(): List<Item> = internalItems.toList()
```

### Regression tests

```kotlin
assertEquals(original, service.items())
```

## KT-H-094: copy shallow state

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Data classes
- Concept: copy shallow state
- Symptom: Nested mutable state is unexpectedly shared.
- Diagnostic goal: Copy nested mutable members or use immutable members.

### Buggy code

```kotlin
val second = first.copy(); second.tags.add("x")
```

### Expected diagnosis

data class copy is shallow; the same mutable tags list is shared.

### Corrected code

```kotlin
data class User(val tags: List<String>)
```

### Regression tests

```kotlin
assertNotSame(first.tags, second.tags)
```

## KT-H-095: collect never completes

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Flows
- Concept: collect never completes
- Symptom: A request waits forever for a hot stream.
- Diagnostic goal: Use a bounded operator for request-scoped collection.

### Buggy code

```kotlin
val value = flow.collect { result = it }
```

### Expected diagnosis

collect is terminal and waits for completion; a hot flow may never complete.

### Corrected code

```kotlin
val value = flow.first()
```

### Regression tests

```kotlin
runTest { assertEquals(expected, flow.first()) }
```

## KT-H-096: runCatching hides cancellation

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Exceptions
- Concept: runCatching hides cancellation
- Symptom: A canceled coroutine continues or reports success.
- Diagnostic goal: Rethrow CancellationException.

### Buggy code

```kotlin
runCatching { suspendWork() }.getOrNull()
```

### Expected diagnosis

Cancellation is a control signal, not an ordinary failure to swallow.

### Corrected code

```kotlin
try { suspendWork() } catch (e: CancellationException) { throw e } catch (e: Exception) { null }
```

### Regression tests

```kotlin
runTest { assertCancellationPropagates() }
```

## KT-H-097: unsafe cast

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Generics
- Concept: unsafe cast
- Symptom: A runtime ClassCastException appears far from input.
- Diagnostic goal: Use a sealed result or checked cast.

### Buggy code

```kotlin
val text = value as String
```

### Expected diagnosis

The cast assumes an unchecked runtime type.

### Corrected code

```kotlin
val text = value as? String ?: return Error.InvalidType
```

### Regression tests

```kotlin
assertEquals(Error.InvalidType, parse(1))
```

## KT-H-098: platform type null

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: JVM interop
- Concept: platform type null
- Symptom: Java API returns null into a non-null declaration.
- Diagnostic goal: Check Java results at the boundary.

### Buggy code

```kotlin
val name: String = javaApi.name
```

### Expected diagnosis

Platform types do not carry Kotlin nullability guarantees.

### Corrected code

```kotlin
val name: String = javaApi.name ?: "unknown"
```

### Regression tests

```kotlin
assertEquals("unknown", adapt(JavaNullApi()))
```

## KT-H-099: shared mutable fixture

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Testing
- Concept: shared mutable fixture
- Symptom: Tests pass alone but fail in a suite.
- Diagnostic goal: Reset or recreate state per test.

### Buggy code

```kotlin
class Test { val cache = mutableMapOf<String,Int>() }
```

### Expected diagnosis

The fixture survives between test methods.

### Corrected code

```kotlin
@BeforeEach fun reset() { cache.clear() }
```

### Regression tests

```kotlin
runAllTestsInRandomOrder()
```

## KT-H-100: default value masks missing field

- Difficulty: Hard
- Language/framework: Kotlin / Kotlin
- Perspective: Serialization
- Concept: default value masks missing field
- Symptom: A breaking API change is silently accepted.
- Diagnostic goal: Distinguish omitted fields from intentional defaults where required.

### Buggy code

```kotlin
data class Request(val enabled: Boolean = false)
```

### Expected diagnosis

A missing enabled property becomes false and hides a contract violation.

### Corrected code

```kotlin
data class Request(val enabled: Boolean)
```

### Regression tests

```kotlin
assertFailsWith<SerializationException> { decode("{}") }
```
