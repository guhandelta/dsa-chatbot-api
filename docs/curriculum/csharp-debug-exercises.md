# C# Debug Exercises

A RAG-training corpus of 300 debugging exercises for C#. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory and ownership, concurrency, API contracts, persistence, validation, security, lifecycle, testing, and deployment

## CS-E-001: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-002: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-003: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-004: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-005: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-006: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-007: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-008: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-009: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-010: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-011: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-012: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-013: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-014: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-015: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-016: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-017: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-018: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-019: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-020: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-021: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-022: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-023: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-024: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-025: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-026: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-027: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-028: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-029: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-030: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-031: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-032: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-033: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-034: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-035: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-036: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-037: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-038: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-039: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-040: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-041: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-042: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-043: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-044: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-045: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-046: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-047: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-048: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-049: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-050: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-051: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-052: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-053: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-054: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-055: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-056: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-057: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-058: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-059: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-060: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-061: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-062: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-063: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-064: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-065: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-066: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-067: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-068: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-069: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-070: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-071: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-072: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-073: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-074: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-075: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-076: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-077: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-078: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-079: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-080: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-081: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-082: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-083: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-084: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-085: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-086: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-087: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-088: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-089: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-090: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-E-091: null dereference

- Difficulty: Easy
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-E-092: missing await

- Difficulty: Easy
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-E-093: deferred query after disposal

- Difficulty: Easy
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-E-094: mutating during foreach

- Difficulty: Easy
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-E-095: owned dependency disposed twice

- Difficulty: Easy
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-E-096: public field omitted

- Difficulty: Easy
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-E-097: catching all exceptions

- Difficulty: Easy
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-E-098: shared mutable singleton

- Difficulty: Easy
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-E-099: missing required setting

- Difficulty: Easy
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-E-100: reference equality

- Difficulty: Easy
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-001: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-002: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-003: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-004: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-005: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-006: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-007: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-008: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-009: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-010: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-011: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-012: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-013: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-014: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-015: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-016: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-017: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-018: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-019: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-020: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-021: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-022: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-023: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-024: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-025: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-026: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-027: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-028: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-029: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-030: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-031: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-032: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-033: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-034: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-035: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-036: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-037: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-038: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-039: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-040: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-041: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-042: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-043: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-044: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-045: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-046: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-047: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-048: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-049: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-050: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-051: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-052: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-053: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-054: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-055: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-056: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-057: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-058: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-059: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-060: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-061: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-062: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-063: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-064: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-065: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-066: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-067: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-068: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-069: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-070: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-071: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-072: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-073: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-074: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-075: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-076: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-077: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-078: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-079: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-080: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-081: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-082: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-083: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-084: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-085: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-086: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-087: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-088: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-089: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-090: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-M-091: null dereference

- Difficulty: Medium
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-M-092: missing await

- Difficulty: Medium
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-M-093: deferred query after disposal

- Difficulty: Medium
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-M-094: mutating during foreach

- Difficulty: Medium
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-M-095: owned dependency disposed twice

- Difficulty: Medium
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-M-096: public field omitted

- Difficulty: Medium
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-M-097: catching all exceptions

- Difficulty: Medium
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-M-098: shared mutable singleton

- Difficulty: Medium
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-M-099: missing required setting

- Difficulty: Medium
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-M-100: reference equality

- Difficulty: Medium
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-001: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-002: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-003: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-004: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-005: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-006: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-007: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-008: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-009: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-010: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-011: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-012: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-013: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-014: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-015: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-016: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-017: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-018: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-019: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-020: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-021: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-022: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-023: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-024: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-025: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-026: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-027: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-028: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-029: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-030: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-031: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-032: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-033: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-034: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-035: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-036: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-037: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-038: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-039: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-040: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-041: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-042: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-043: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-044: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-045: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-046: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-047: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-048: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-049: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-050: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-051: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-052: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-053: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-054: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-055: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-056: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-057: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-058: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-059: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-060: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-061: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-062: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-063: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-064: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-065: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-066: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-067: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-068: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-069: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-070: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-071: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-072: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-073: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-074: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-075: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-076: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-077: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-078: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-079: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-080: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-081: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-082: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-083: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-084: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-085: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-086: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-087: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-088: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-089: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-090: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```

## CS-H-091: null dereference

- Difficulty: Hard
- Language/platform: C#
- Perspective: Nullability
- Concept: null dereference
- Symptom: A request fails with NullReferenceException.
- Diagnostic goal: Validate nullable values before dereferencing.

### Buggy code

```csharp
string name1 = user.Profile.Name;
```

### Expected diagnosis

The compiler/runtime contract does not guarantee Profile or Name exists.

### Corrected code

```csharp
string name1 = user.Profile?.Name ?? "unknown";
```

### Regression tests

```csharp
// Null profile yields 'unknown'; populated profile yields its name.
```

## CS-H-092: missing await

- Difficulty: Hard
- Language/platform: C#
- Perspective: Async
- Concept: missing await
- Symptom: The caller receives a task instead of a result.
- Diagnostic goal: Await the asynchronous operation and propagate cancellation.

### Buggy code

```csharp
public string Load1() => client.GetStringAsync(url).Result;
```

### Expected diagnosis

Blocking on Result can deadlock a synchronization context and hides asynchronous failure.

### Corrected code

```csharp
public async Task<string> Load1(CancellationToken token) => await client.GetStringAsync(url, token);
```

### Regression tests

```csharp
// Cancellation is propagated and no synchronous wait occurs.
```

## CS-H-093: deferred query after disposal

- Difficulty: Hard
- Language/platform: C#
- Perspective: LINQ
- Concept: deferred query after disposal
- Symptom: Enumeration fails after the data source is closed.
- Diagnostic goal: Materialize inside the resource lifetime when needed.

### Buggy code

```csharp
IEnumerable<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name); }
```

### Expected diagnosis

LINQ is deferred; the returned query enumerates after db is disposed.

### Corrected code

```csharp
IReadOnlyList<string> Names1() { using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }
```

### Regression tests

```csharp
// The returned list remains usable after the context closes.
```

## CS-H-094: mutating during foreach

- Difficulty: Hard
- Language/platform: C#
- Perspective: Collections
- Concept: mutating during foreach
- Symptom: InvalidOperationException is thrown.
- Diagnostic goal: Build a removal list or iterate a snapshot.

### Buggy code

```csharp
foreach (var item in items) if (item.IsExpired) items.Remove(item);
```

### Expected diagnosis

List enumeration detects structural modification.

### Corrected code

```csharp
items.RemoveAll(item => item.IsExpired);
```

### Regression tests

```csharp
// All expired items are removed and active items remain.
```

## CS-H-095: owned dependency disposed twice

- Difficulty: Hard
- Language/platform: C#
- Perspective: Disposal
- Concept: owned dependency disposed twice
- Symptom: A shared stream fails when another component uses it.
- Diagnostic goal: Make ownership explicit and dispose only the owner.

### Buggy code

```csharp
using var stream = sharedStream;
Read(stream);
```

### Expected diagnosis

Disposing a borrowed resource invalidates the component that owns it.

### Corrected code

```csharp
Read(sharedStream);
```

### Regression tests

```csharp
// The owner remains responsible for disposing sharedStream.
```

## CS-H-096: public field omitted

- Difficulty: Hard
- Language/platform: C#
- Perspective: Serialization
- Concept: public field omitted
- Symptom: JSON lacks a required property.
- Diagnostic goal: Configure the serializer contract or use properties.

### Buggy code

```csharp
public class Item1 { public int id; }
```

### Expected diagnosis

The default serializer contract commonly includes public properties, not fields.

### Corrected code

```csharp
public class Item1 { public int Id { get; set; } }
```

### Regression tests

```csharp
// Serialized JSON contains the expected Id property.
```

## CS-H-097: catching all exceptions

- Difficulty: Hard
- Language/platform: C#
- Perspective: Exceptions
- Concept: catching all exceptions
- Symptom: Programming defects become success responses.
- Diagnostic goal: Catch only expected failures and preserve diagnostics.

### Buggy code

```csharp
try { Save(); } catch (Exception) { return true; }
```

### Expected diagnosis

Catching Exception hides cancellation, bugs, and environmental failures.

### Corrected code

```csharp
try { Save(); return true; } catch (ValidationException) { return false; }
```

### Regression tests

```csharp
// Validation failure is reported; unexpected exceptions propagate.
```

## CS-H-098: shared mutable singleton

- Difficulty: Hard
- Language/platform: C#
- Perspective: Concurrency
- Concept: shared mutable singleton
- Symptom: Requests observe one another's state.
- Diagnostic goal: Use scoped state or synchronization for mutable data.

### Buggy code

```csharp
services.AddSingleton<Cart1>();
```

### Expected diagnosis

A singleton carrying per-user mutable state is shared across all requests.

### Corrected code

```csharp
services.AddScoped<Cart1>();
```

### Regression tests

```csharp
// Two scopes receive independent carts.
```

## CS-H-099: missing required setting

- Difficulty: Hard
- Language/platform: C#
- Perspective: Configuration
- Concept: missing required setting
- Symptom: The app starts and fails later with a null value.
- Diagnostic goal: Validate configuration at startup.

### Buggy code

```csharp
var url1 = config["ServiceUrl"];
client.BaseAddress = new Uri(url1);
```

### Expected diagnosis

A missing setting becomes a delayed null/format failure.

### Corrected code

```csharp
var url1 = config["ServiceUrl"] ?? throw new InvalidOperationException("ServiceUrl required");
client.BaseAddress = new Uri(url1);
```

### Regression tests

```csharp
// Startup fails clearly when ServiceUrl is absent.
```

## CS-H-100: reference equality

- Difficulty: Hard
- Language/platform: C#
- Perspective: Equality
- Concept: reference equality
- Symptom: Equivalent value objects do not compare equal.
- Diagnostic goal: Implement value equality or use a value type/record.

### Buggy code

```csharp
class Point1 { public int X; public int Y; }
if (a == b) { ... }
```

### Expected diagnosis

Classes default to reference equality unless equality is overridden.

### Corrected code

```csharp
record Point1(int X, int Y);
if (a == b) { ... }
```

### Regression tests

```csharp
// Two Point1(1,2) values compare equal.
```
