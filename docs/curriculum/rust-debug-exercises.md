# Rust Debug Exercises

A RAG-training corpus of 300 debugging exercises for Rust. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, state, memory/ownership, concurrency, errors, APIs, security, persistence, and testing

## RUST-E-001: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-002: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-003: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-004: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-005: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-006: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-007: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-008: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-009: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-010: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-011: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-012: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-013: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-014: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-015: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-016: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-017: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-018: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-019: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-020: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-021: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-022: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-023: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-024: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-025: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-026: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-027: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-028: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-029: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-030: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-031: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-032: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-033: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-034: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-035: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-036: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-037: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-038: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-039: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-040: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-041: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-042: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-043: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-044: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-045: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-046: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-047: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-048: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-049: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-050: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-051: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-052: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-053: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-054: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-055: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-056: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-057: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-058: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-059: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-060: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-061: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-062: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-063: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-064: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-065: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-066: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-067: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-068: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-069: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-070: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-071: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-072: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-073: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-074: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-075: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-076: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-077: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-078: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-079: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-080: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-081: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-082: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-083: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-084: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-085: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-086: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-087: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-088: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-089: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-090: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-E-091: use after move

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-E-092: mutable and immutable borrow overlap

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-E-093: unwrap at boundary

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-E-094: return reference to local

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-E-095: iterator consumed twice

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-E-096: data race across threads

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-E-097: blocking executor thread

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-E-098: None treated as value

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-E-099: unbounded Vec growth

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-E-100: stringly typed errors

- Difficulty: Easy
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-001: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-002: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-003: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-004: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-005: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-006: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-007: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-008: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-009: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-010: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-011: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-012: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-013: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-014: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-015: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-016: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-017: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-018: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-019: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-020: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-021: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-022: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-023: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-024: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-025: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-026: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-027: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-028: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-029: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-030: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-031: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-032: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-033: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-034: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-035: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-036: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-037: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-038: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-039: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-040: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-041: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-042: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-043: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-044: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-045: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-046: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-047: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-048: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-049: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-050: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-051: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-052: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-053: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-054: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-055: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-056: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-057: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-058: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-059: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-060: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-061: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-062: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-063: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-064: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-065: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-066: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-067: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-068: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-069: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-070: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-071: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-072: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-073: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-074: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-075: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-076: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-077: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-078: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-079: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-080: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-081: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-082: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-083: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-084: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-085: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-086: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-087: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-088: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-089: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-090: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-M-091: use after move

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-M-092: mutable and immutable borrow overlap

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-M-093: unwrap at boundary

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-M-094: return reference to local

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-M-095: iterator consumed twice

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-M-096: data race across threads

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-M-097: blocking executor thread

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-M-098: None treated as value

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-M-099: unbounded Vec growth

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-M-100: stringly typed errors

- Difficulty: Medium
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-001: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-002: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-003: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-004: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-005: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-006: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-007: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-008: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-009: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-010: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-011: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-012: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-013: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-014: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-015: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-016: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-017: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-018: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-019: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-020: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-021: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-022: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-023: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-024: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-025: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-026: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-027: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-028: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-029: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-030: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-031: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-032: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-033: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-034: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-035: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-036: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-037: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-038: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-039: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-040: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-041: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-042: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-043: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-044: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-045: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-046: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-047: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-048: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-049: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-050: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-051: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-052: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-053: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-054: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-055: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-056: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-057: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-058: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-059: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-060: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-061: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-062: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-063: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-064: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-065: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-066: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-067: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-068: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-069: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-070: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-071: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-072: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-073: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-074: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-075: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-076: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-077: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-078: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-079: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-080: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-081: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-082: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-083: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-084: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-085: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-086: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-087: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-088: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-089: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-090: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```

## RUST-H-091: use after move

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Ownership
- Concept: use after move
- Symptom: The compiler rejects a later use.
- Diagnostic goal: Borrow when ownership should remain with the caller.

### Buggy code

```rust
let name = String::from("Ada");
consume(name);
println!("{name}");
```

### Expected diagnosis

Passing String by value moves it into consume.

### Corrected code

```rust
let name = String::from("Ada");
consume(&name);
println!("{name}");
```

### Regression tests

```rust
assert_eq!(display(), "Ada")
```

## RUST-H-092: mutable and immutable borrow overlap

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Borrowing
- Concept: mutable and immutable borrow overlap
- Symptom: Compilation fails or a refactor risks invalidation.
- Diagnostic goal: End the immutable borrow before mutating the collection.

### Buggy code

```rust
let first = &items[0];
items.push(4);
println!("{first}");
```

### Expected diagnosis

push may reallocate, so an outstanding reference cannot remain valid across it.

### Corrected code

```rust
let first = items[0];
items.push(4);
println!("{first}");
```

### Regression tests

```rust
assert_eq!(safe(), 1)
```

## RUST-H-093: unwrap at boundary

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Result handling
- Concept: unwrap at boundary
- Symptom: Malformed input crashes the service.
- Diagnostic goal: Propagate or map errors at the boundary.

### Buggy code

```rust
let port: u16 = input.parse().unwrap();
```

### Expected diagnosis

User or configuration input can fail to parse; unwrap turns expected failure into a panic.

### Corrected code

```rust
let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;
```

### Regression tests

```rust
assert!(invalid_port().is_err())
```

## RUST-H-094: return reference to local

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Lifetimes
- Concept: return reference to local
- Symptom: The compiler rejects a dangling reference.
- Diagnostic goal: Return owned data or borrow from an input with a declared lifetime.

### Buggy code

```rust
fn label() -> &str { let value = String::from("ok"); &value }
```

### Expected diagnosis

value is dropped at function exit.

### Corrected code

```rust
fn label() -> String { String::from("ok") }
```

### Regression tests

```rust
assert_eq!(label(), "ok")
```

## RUST-H-095: iterator consumed twice

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Iterators
- Concept: iterator consumed twice
- Symptom: The second pass is empty.
- Diagnostic goal: Create a new iterator or collect when repeated traversal is required.

### Buggy code

```rust
let values = nums.iter().map(|n| n * 2);
let a: Vec<_> = values.collect();
let b: Vec<_> = values.collect();
```

### Expected diagnosis

Iterator values are consumed by collect.

### Corrected code

```rust
let a: Vec<_> = nums.iter().map(|n| n * 2).collect();
let b: Vec<_> = nums.iter().map(|n| n * 2).collect();
```

### Regression tests

```rust
assert_eq!(a, b)
```

## RUST-H-096: data race across threads

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Concurrency
- Concept: data race across threads
- Symptom: The compiler rejects shared mutable access.
- Diagnostic goal: Use Arc plus a synchronization primitive.

### Buggy code

```rust
let mut count = 0;
thread::spawn(|| count += 1);
```

### Expected diagnosis

Threads cannot safely share a mutable stack variable without ownership and synchronization.

### Corrected code

```rust
let count = Arc::new(Mutex::new(0));
let worker = Arc::clone(&count);
thread::spawn(move || *worker.lock().unwrap() += 1);
```

### Regression tests

```rust
assert_eq!(*count.lock().unwrap(), 1)
```

## RUST-H-097: blocking executor thread

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Async
- Concept: blocking executor thread
- Symptom: Unrelated futures stop making progress.
- Diagnostic goal: Use an async operation or move blocking work to a dedicated pool.

### Buggy code

```rust
async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }
```

### Expected diagnosis

Blocking the executor thread prevents other tasks from being polled.

### Corrected code

```rust
async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }
```

### Regression tests

```rust
assert_concurrent_tasks_progress()
```

## RUST-H-098: None treated as value

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Option
- Concept: None treated as value
- Symptom: A missing record causes a panic.
- Diagnostic goal: Map or handle absence explicitly.

### Buggy code

```rust
let user = users.get(&id).unwrap();
```

### Expected diagnosis

A missing key is a normal domain outcome, not necessarily a programmer error.

### Corrected code

```rust
let user = users.get(&id).ok_or(Error::NotFound)?;
```

### Regression tests

```rust
assert!(missing_user().is_err())
```

## RUST-H-099: unbounded Vec growth

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Memory
- Concept: unbounded Vec growth
- Symptom: A service eventually exhausts memory.
- Diagnostic goal: Bound input before allocation.

### Buggy code

```rust
let mut body = Vec::new();
reader.read_to_end(&mut body)?;
```

### Expected diagnosis

An untrusted stream can grow the vector without a limit.

### Corrected code

```rust
let mut body = Vec::with_capacity(MAX);
reader.take((MAX + 1) as u64).read_to_end(&mut body)?;
if body.len() > MAX { return Err(Error::TooLarge); }
```

### Regression tests

```rust
assert!(oversized_body().is_err())
```

## RUST-H-100: stringly typed errors

- Difficulty: Hard
- Language/framework: Rust / Rust
- Perspective: Error design
- Concept: stringly typed errors
- Symptom: Callers cannot reliably classify failures.
- Diagnostic goal: Use an enum with source errors and stable variants.

### Buggy code

```rust
return Err(format!("db: {err}"));
```

### Expected diagnosis

A string loses machine-readable category and source context.

### Corrected code

```rust
#[derive(thiserror::Error, Debug)]
enum Error { #[error("database error: {0}")] Db(#[from] DbError) }
```

### Regression tests

```rust
assert_matches!(db_failure(), Err(Error::Db(_)))
```
