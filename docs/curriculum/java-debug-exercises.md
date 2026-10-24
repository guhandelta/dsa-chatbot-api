# Java Debug Exercises

A RAG-training corpus of 300 debugging exercises for Java. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory, ownership, concurrency, timing, APIs, errors, security, persistence, and testing

## JAVA-E-001: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-002: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-003: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-004: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-005: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-006: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-007: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-008: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-009: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-010: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-011: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-012: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-013: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-014: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-015: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-016: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-017: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-018: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-019: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-020: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-021: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-022: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-023: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-024: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-025: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-026: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-027: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-028: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-029: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-030: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-031: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-032: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-033: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-034: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-035: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-036: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-037: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-038: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-039: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-040: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-041: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-042: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-043: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-044: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-045: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-046: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-047: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-048: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-049: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-050: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-051: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-052: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-053: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-054: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-055: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-056: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-057: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-058: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-059: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-060: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-061: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-062: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-063: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-064: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-065: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-066: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-067: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-068: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-069: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-070: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-071: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-072: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-073: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-074: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-075: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-076: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-077: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-078: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-079: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-080: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-081: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-082: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-083: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-084: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-085: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-086: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-087: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-088: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-089: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-090: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-E-091: mutable list alias

- Difficulty: Easy
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-E-092: null dereference

- Difficulty: Easy
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-E-093: catch and ignore

- Difficulty: Easy
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-E-094: check then act race

- Difficulty: Easy
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-E-095: stream reused

- Difficulty: Easy
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-E-096: reader not closed

- Difficulty: Easy
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-E-097: raw collection

- Difficulty: Easy
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-E-098: reference comparison

- Difficulty: Easy
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-E-099: integer division

- Difficulty: Easy
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-E-100: unbounded cache

- Difficulty: Easy
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-001: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-002: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-003: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-004: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-005: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-006: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-007: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-008: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-009: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-010: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-011: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-012: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-013: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-014: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-015: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-016: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-017: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-018: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-019: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-020: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-021: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-022: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-023: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-024: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-025: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-026: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-027: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-028: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-029: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-030: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-031: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-032: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-033: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-034: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-035: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-036: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-037: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-038: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-039: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-040: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-041: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-042: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-043: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-044: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-045: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-046: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-047: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-048: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-049: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-050: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-051: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-052: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-053: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-054: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-055: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-056: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-057: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-058: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-059: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-060: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-061: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-062: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-063: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-064: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-065: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-066: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-067: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-068: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-069: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-070: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-071: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-072: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-073: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-074: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-075: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-076: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-077: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-078: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-079: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-080: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-081: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-082: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-083: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-084: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-085: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-086: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-087: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-088: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-089: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-090: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-M-091: mutable list alias

- Difficulty: Medium
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-M-092: null dereference

- Difficulty: Medium
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-M-093: catch and ignore

- Difficulty: Medium
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-M-094: check then act race

- Difficulty: Medium
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-M-095: stream reused

- Difficulty: Medium
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-M-096: reader not closed

- Difficulty: Medium
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-M-097: raw collection

- Difficulty: Medium
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-M-098: reference comparison

- Difficulty: Medium
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-M-099: integer division

- Difficulty: Medium
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-M-100: unbounded cache

- Difficulty: Medium
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-001: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-002: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-003: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-004: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-005: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-006: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-007: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-008: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-009: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-010: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-011: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-012: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-013: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-014: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-015: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-016: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-017: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-018: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-019: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-020: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-021: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-022: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-023: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-024: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-025: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-026: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-027: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-028: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-029: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-030: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-031: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-032: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-033: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-034: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-035: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-036: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-037: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-038: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-039: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-040: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-041: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-042: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-043: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-044: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-045: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-046: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-047: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-048: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-049: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-050: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-051: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-052: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-053: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-054: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-055: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-056: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-057: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-058: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-059: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-060: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-061: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-062: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-063: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-064: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-065: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-066: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-067: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-068: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-069: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-070: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-071: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-072: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-073: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-074: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-075: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-076: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-077: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-078: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-079: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-080: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-081: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-082: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-083: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-084: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-085: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-086: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-087: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-088: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-089: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-090: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```

## JAVA-H-091: mutable list alias

- Difficulty: Hard
- Language/platform: Java
- Perspective: Collections
- Concept: mutable list alias
- Symptom: A caller observes later internal changes.
- Diagnostic goal: Copy at an ownership boundary.

### Buggy code

```java
this.items = items;
```

### Expected diagnosis

The field aliases the caller-owned mutable list.

### Corrected code

```java
this.items = List.copyOf(items);
```

### Regression tests

```java
assertEquals(List.of(1,2), object.items());
```

## JAVA-H-092: null dereference

- Difficulty: Hard
- Language/platform: Java
- Perspective: Null safety
- Concept: null dereference
- Symptom: A missing value crashes a request.
- Diagnostic goal: Represent absence explicitly.

### Buggy code

```java
return user.getProfile().getName();
```

### Expected diagnosis

A nested nullable value is dereferenced without a contract.

### Corrected code

```java
return user.getProfile().map(Profile::getName).orElse("unknown");
```

### Regression tests

```java
assertEquals("unknown", display(userWithoutProfile));
```

## JAVA-H-093: catch and ignore

- Difficulty: Hard
- Language/platform: Java
- Perspective: Exceptions
- Concept: catch and ignore
- Symptom: A failed operation appears successful.
- Diagnostic goal: Preserve failure and context.

### Buggy code

```java
try { save(); } catch (Exception e) { }
```

### Expected diagnosis

Swallowing exceptions leaves callers unable to distinguish success from failure.

### Corrected code

```java
try { save(); } catch (IOException e) { throw new StorageException("save failed", e); }
```

### Regression tests

```java
assertThrows(StorageException.class, () -> failingSave());
```

## JAVA-H-094: check then act race

- Difficulty: Hard
- Language/platform: Java
- Perspective: Concurrency
- Concept: check then act race
- Symptom: Two threads allocate the same slot.
- Diagnostic goal: Make the invariant atomic.

### Buggy code

```java
if (!slots.contains(key)) slots.add(key);
```

### Expected diagnosis

The check and mutation can interleave between threads.

### Corrected code

```java
synchronized (slots) { if (!slots.contains(key)) slots.add(key); }
```

### Regression tests

```java
runConcurrentAllocationAndAssertOneEntry();
```

## JAVA-H-095: stream reused

- Difficulty: Hard
- Language/platform: Java
- Perspective: Streams
- Concept: stream reused
- Symptom: A second terminal operation fails.
- Diagnostic goal: Create a fresh stream for each traversal.

### Buggy code

```java
Stream<String> stream = names.stream(); stream.count(); stream.findFirst();
```

### Expected diagnosis

Streams are single-use pipelines consumed by a terminal operation.

### Corrected code

```java
long count = names.stream().count(); Optional<String> first = names.stream().findFirst();
```

### Regression tests

```java
assertEquals(2, count); assertTrue(first.isPresent());
```

## JAVA-H-096: reader not closed

- Difficulty: Hard
- Language/platform: Java
- Perspective: Resources
- Concept: reader not closed
- Symptom: File descriptors remain open on error.
- Diagnostic goal: Use try-with-resources.

### Buggy code

```java
Reader r = Files.newBufferedReader(path); return r.readLine();
```

### Expected diagnosis

An exception or return path skips close.

### Corrected code

```java
try (Reader r = Files.newBufferedReader(path)) { return new BufferedReader(r).readLine(); }
```

### Regression tests

```java
assertNoOpenHandleAfterReadAndFailure();
```

## JAVA-H-097: raw collection

- Difficulty: Hard
- Language/platform: Java
- Perspective: Generics
- Concept: raw collection
- Symptom: A cast fails far from insertion.
- Diagnostic goal: Preserve type information at the boundary.

### Buggy code

```java
List values = new ArrayList(); values.add("x"); Integer n = (Integer) values.get(0);
```

### Expected diagnosis

Raw types disable compile-time element checks.

### Corrected code

```java
List<String> values = new ArrayList<>(); values.add("x"); String s = values.get(0);
```

### Regression tests

```java
assertEquals("x", s);
```

## JAVA-H-098: reference comparison

- Difficulty: Hard
- Language/platform: Java
- Perspective: Equality
- Concept: reference comparison
- Symptom: Equal strings do not match.
- Diagnostic goal: Use value equality for objects.

### Buggy code

```java
if (input == "yes") accept();
```

### Expected diagnosis

== compares references for String, not contents.

### Corrected code

```java
if ("yes".equals(input)) accept();
```

### Regression tests

```java
assertAccepted(new String("yes"));
```

## JAVA-H-099: integer division

- Difficulty: Hard
- Language/platform: Java
- Perspective: Numeric correctness
- Concept: integer division
- Symptom: A percentage is always zero.
- Diagnostic goal: Promote before division.

### Buggy code

```java
double ratio = completed / total;
```

### Expected diagnosis

Both operands are integers, so division truncates before assignment.

### Corrected code

```java
double ratio = (double) completed / total;
```

### Regression tests

```java
assertEquals(0.5, ratio);
```

## JAVA-H-100: unbounded cache

- Difficulty: Hard
- Language/platform: Java
- Perspective: JVM behavior
- Concept: unbounded cache
- Symptom: Memory grows until OutOfMemoryError.
- Diagnostic goal: Bound cache lifetime and size.

### Buggy code

```java
static final Map<String, byte[]> CACHE = new HashMap<>();
```

### Expected diagnosis

A process-wide map retains every key forever.

### Corrected code

```java
static final Cache<String, byte[]> CACHE = Caffeine.newBuilder().maximumSize(1000).build();
```

### Regression tests

```java
assertCacheEvictsAfterBound();
```
