# C++ Debug Exercises

A RAG-training corpus of 300 debugging exercises for C++. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory and ownership, concurrency, API contracts, persistence, validation, security, lifecycle, testing, and deployment

## CPP-E-001: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-002: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-003: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-004: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-005: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-006: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-007: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-008: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-009: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-010: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-011: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-012: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-013: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-014: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-015: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-016: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-017: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-018: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-019: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-020: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-021: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-022: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-023: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-024: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-025: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-026: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-027: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-028: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-029: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-030: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-031: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-032: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-033: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-034: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-035: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-036: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-037: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-038: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-039: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-040: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-041: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-042: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-043: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-044: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-045: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-046: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-047: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-048: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-049: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-050: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-051: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-052: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-053: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-054: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-055: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-056: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-057: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-058: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-059: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-060: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-061: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-062: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-063: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-064: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-065: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-066: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-067: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-068: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-069: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-070: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-071: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-072: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-073: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-074: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-075: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-076: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-077: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-078: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-079: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-080: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-081: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-082: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-083: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-084: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-085: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-086: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-087: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-088: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-089: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-090: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-E-091: manual cleanup

- Difficulty: Easy
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-E-092: use after move

- Difficulty: Easy
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-E-093: erase invalidates iterator

- Difficulty: Easy
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-E-094: dangling reference

- Difficulty: Easy
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-E-095: partial mutation

- Difficulty: Easy
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-E-096: shared ownership cycle

- Difficulty: Easy
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-E-097: mutex not exception safe

- Difficulty: Easy
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-E-098: unsigned underflow

- Difficulty: Easy
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-E-099: missing virtual destructor

- Difficulty: Easy
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-E-100: copying expensive object

- Difficulty: Easy
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-001: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-002: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-003: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-004: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-005: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-006: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-007: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-008: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-009: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-010: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-011: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-012: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-013: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-014: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-015: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-016: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-017: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-018: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-019: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-020: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-021: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-022: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-023: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-024: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-025: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-026: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-027: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-028: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-029: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-030: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-031: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-032: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-033: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-034: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-035: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-036: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-037: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-038: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-039: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-040: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-041: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-042: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-043: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-044: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-045: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-046: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-047: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-048: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-049: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-050: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-051: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-052: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-053: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-054: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-055: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-056: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-057: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-058: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-059: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-060: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-061: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-062: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-063: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-064: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-065: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-066: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-067: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-068: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-069: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-070: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-071: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-072: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-073: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-074: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-075: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-076: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-077: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-078: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-079: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-080: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-081: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-082: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-083: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-084: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-085: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-086: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-087: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-088: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-089: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-090: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-M-091: manual cleanup

- Difficulty: Medium
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-M-092: use after move

- Difficulty: Medium
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-M-093: erase invalidates iterator

- Difficulty: Medium
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-M-094: dangling reference

- Difficulty: Medium
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-M-095: partial mutation

- Difficulty: Medium
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-M-096: shared ownership cycle

- Difficulty: Medium
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-M-097: mutex not exception safe

- Difficulty: Medium
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-M-098: unsigned underflow

- Difficulty: Medium
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-M-099: missing virtual destructor

- Difficulty: Medium
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-M-100: copying expensive object

- Difficulty: Medium
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-001: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-002: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-003: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-004: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-005: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-006: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-007: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-008: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-009: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-010: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-011: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-012: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-013: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-014: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-015: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-016: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-017: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-018: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-019: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-020: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-021: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-022: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-023: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-024: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-025: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-026: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-027: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-028: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-029: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-030: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-031: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-032: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-033: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-034: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-035: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-036: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-037: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-038: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-039: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-040: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-041: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-042: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-043: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-044: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-045: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-046: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-047: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-048: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-049: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-050: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-051: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-052: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-053: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-054: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-055: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-056: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-057: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-058: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-059: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-060: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-061: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-062: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-063: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-064: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-065: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-066: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-067: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-068: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-069: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-070: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-071: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-072: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-073: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-074: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-075: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-076: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-077: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-078: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-079: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-080: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-081: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-082: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-083: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-084: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-085: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-086: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-087: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-088: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-089: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-090: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```

## CPP-H-091: manual cleanup

- Difficulty: Hard
- Language/platform: C++
- Perspective: RAII
- Concept: manual cleanup
- Symptom: An exception leaks a resource.
- Diagnostic goal: Bind ownership to an object lifetime.

### Buggy code

```cpp
FILE *file1 = fopen(path, "r");
if (!file1) throw std::runtime_error("open");
process(file1);
fclose(file1);
```

### Expected diagnosis

An exception from process skips fclose.

### Corrected code

```cpp
struct FileCloser1 { void operator()(FILE *p) const { if (p) fclose(p); } };
using File1 = std::unique_ptr<FILE, FileCloser1>;
File1 file1(fopen(path, "r"));
if (!file1) throw std::runtime_error("open");
process(file1.get());
```

### Regression tests

```cpp
// Throw from process and verify the file is still closed.
```

## CPP-H-092: use after move

- Difficulty: Hard
- Language/platform: C++
- Perspective: Move semantics
- Concept: use after move
- Symptom: The source object is assumed to retain its value.
- Diagnostic goal: Treat moved-from objects as valid but unspecified.

### Buggy code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(first1);
```

### Expected diagnosis

Moving transfers resources; using the source as if it still contains the old value is a contract error.

### Corrected code

```cpp
std::string first1 = "data";
std::string second1 = std::move(first1);
use(second1);
```

### Regression tests

```cpp
// Assert second1 contains data; do not depend on first1's value.
```

## CPP-H-093: erase invalidates iterator

- Difficulty: Hard
- Language/platform: C++
- Perspective: Iterator validity
- Concept: erase invalidates iterator
- Symptom: The loop skips elements or crashes.
- Diagnostic goal: Use the iterator returned by erase.

### Buggy code

```cpp
for (auto it = values.begin(); it != values.end(); ++it) {
    if (*it < 0) values.erase(it);
}
```

### Expected diagnosis

erase invalidates it; incrementing it afterward is undefined behavior.

### Corrected code

```cpp
for (auto it = values.begin(); it != values.end();) {
    if (*it < 0) it = values.erase(it);
    else ++it;
}
```

### Regression tests

```cpp
// [-1,-2,3] becomes [3] without invalid iterator use.
```

## CPP-H-094: dangling reference

- Difficulty: Hard
- Language/platform: C++
- Perspective: Templates
- Concept: dangling reference
- Symptom: A returned reference points to a temporary.
- Diagnostic goal: Return by value or reference only to an object with sufficient lifetime.

### Buggy code

```cpp
const std::string& label1() { return std::string("ok"); }
```

### Expected diagnosis

The temporary is destroyed at the end of the return expression.

### Corrected code

```cpp
std::string label1() { return std::string("ok"); }
```

### Regression tests

```cpp
assert(label1() == "ok");
```

## CPP-H-095: partial mutation

- Difficulty: Hard
- Language/platform: C++
- Perspective: Exception safety
- Concept: partial mutation
- Symptom: An operation leaves an object half updated.
- Diagnostic goal: Prepare changes before committing them.

### Buggy code

```cpp
void rename1(User &u, std::string name) { u.name = std::move(name); validate(u); }
```

### Expected diagnosis

If validation throws, the object has already been mutated.

### Corrected code

```cpp
void rename1(User &u, std::string name) {
    User candidate = u;
    candidate.name = std::move(name);
    validate(candidate);
    u = std::move(candidate);
}
```

### Regression tests

```cpp
// Invalid names leave u unchanged.
```

## CPP-H-096: shared ownership cycle

- Difficulty: Hard
- Language/platform: C++
- Perspective: Ownership
- Concept: shared ownership cycle
- Symptom: Objects are never destroyed.
- Diagnostic goal: Use weak_ptr for non-owning back references.

### Buggy code

```cpp
struct Node1 { std::shared_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Expected diagnosis

A parent-child cycle keeps both reference counts nonzero.

### Corrected code

```cpp
struct Node1 { std::weak_ptr<Node1> parent; std::shared_ptr<Node1> child; };
```

### Regression tests

```cpp
// Destroying the root releases the child graph.
```

## CPP-H-097: mutex not exception safe

- Difficulty: Hard
- Language/platform: C++
- Perspective: Concurrency
- Concept: mutex not exception safe
- Symptom: A thrown operation deadlocks later callers.
- Diagnostic goal: Use scoped locking.

### Buggy code

```cpp
mutex.lock();
update();
mutex.unlock();
```

### Expected diagnosis

An exception skips unlock.

### Corrected code

```cpp
std::lock_guard<std::mutex> guard(mutex);
update();
```

### Regression tests

```cpp
// Throwing from update still permits a later lock.
```

## CPP-H-098: unsigned underflow

- Difficulty: Hard
- Language/platform: C++
- Perspective: Numeric correctness
- Concept: unsigned underflow
- Symptom: A reverse loop never terminates.
- Diagnostic goal: Use a signed index or an iterator for reverse traversal.

### Buggy code

```cpp
for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);
```

### Expected diagnosis

size_t cannot become negative, so the condition remains true after zero.

### Corrected code

```cpp
for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);
```

### Regression tests

```cpp
// Empty and one-element vectors both terminate.
```

## CPP-H-099: missing virtual destructor

- Difficulty: Hard
- Language/platform: C++
- Perspective: Polymorphism
- Concept: missing virtual destructor
- Symptom: Deleting through a base pointer leaks derived resources.
- Diagnostic goal: Make a polymorphic base destructor virtual.

### Buggy code

```cpp
struct Base1 { ~Base1() {} virtual void run() = 0; };
```

### Expected diagnosis

Deleting a derived object through Base without a virtual destructor is undefined behavior.

### Corrected code

```cpp
struct Base1 { virtual ~Base1() = default; virtual void run() = 0; };
```

### Regression tests

```cpp
// unique_ptr<Base1> destroys a derived instance completely.
```

## CPP-H-100: copying expensive object

- Difficulty: Hard
- Language/platform: C++
- Perspective: API contract
- Concept: copying expensive object
- Symptom: A hot path allocates unexpectedly.
- Diagnostic goal: Pass large read-only values by const reference.

### Buggy code

```cpp
void inspect1(std::vector<int> values) { use(values); }
```

### Expected diagnosis

Passing by value copies the vector and may allocate.

### Corrected code

```cpp
void inspect1(const std::vector<int>& values) { use(values); }
```

### Regression tests

```cpp
// Instrumented vector confirms no copy occurs.
```
