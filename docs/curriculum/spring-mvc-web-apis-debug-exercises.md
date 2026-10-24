# Spring MVC & Web APIs Debug Exercises

A RAG-training corpus of 300 debugging exercises for Spring MVC & Web APIs. Each record contains framework-specific metadata, a failure example, an editorial diagnosis, corrected Java/Spring code, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: configuration, lifecycle, proxies, persistence, HTTP contracts, security, testing, transactions, observability, and deployment

## MVC-E-001: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-002: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-003: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-004: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-005: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-006: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-007: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-008: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-009: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-010: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-011: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-012: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-013: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-014: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-015: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-016: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-017: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-018: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-019: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-020: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-021: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-022: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-023: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-024: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-025: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-026: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-027: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-028: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-029: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-030: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-031: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-032: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-033: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-034: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-035: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-036: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-037: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-038: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-039: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-040: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-041: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-042: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-043: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-044: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-045: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-046: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-047: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-048: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-049: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-050: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-051: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-052: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-053: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-054: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-055: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-056: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-057: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-058: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-059: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-060: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-061: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-062: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-063: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-064: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-065: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-066: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-067: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-068: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-069: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-070: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-071: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-072: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-073: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-074: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-075: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-076: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-077: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-078: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-079: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-080: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-081: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-082: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-083: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-084: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-085: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-086: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-087: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-088: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-089: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-090: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-E-091: missing @RequestBody

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-E-092: constraints never execute

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-E-093: always returns 200

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-E-094: controller catches every exception

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-E-095: wrong media type

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-E-096: wildcard with credentials

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-E-097: entity exposed directly

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-E-098: retry creates duplicates

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-E-099: large file buffered

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-E-100: user path traversal

- Difficulty: Easy
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-001: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-002: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-003: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-004: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-005: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-006: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-007: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-008: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-009: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-010: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-011: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-012: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-013: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-014: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-015: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-016: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-017: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-018: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-019: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-020: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-021: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-022: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-023: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-024: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-025: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-026: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-027: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-028: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-029: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-030: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-031: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-032: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-033: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-034: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-035: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-036: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-037: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-038: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-039: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-040: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-041: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-042: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-043: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-044: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-045: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-046: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-047: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-048: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-049: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-050: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-051: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-052: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-053: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-054: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-055: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-056: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-057: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-058: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-059: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-060: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-061: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-062: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-063: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-064: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-065: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-066: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-067: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-068: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-069: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-070: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-071: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-072: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-073: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-074: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-075: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-076: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-077: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-078: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-079: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-080: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-081: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-082: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-083: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-084: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-085: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-086: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-087: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-088: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-089: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-090: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-M-091: missing @RequestBody

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-M-092: constraints never execute

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-M-093: always returns 200

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-M-094: controller catches every exception

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-M-095: wrong media type

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-M-096: wildcard with credentials

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-M-097: entity exposed directly

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-M-098: retry creates duplicates

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-M-099: large file buffered

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-M-100: user path traversal

- Difficulty: Medium
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-001: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-002: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-003: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-004: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-005: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-006: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-007: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-008: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-009: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-010: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-011: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-012: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-013: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-014: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-015: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-016: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-017: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-018: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-019: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-020: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-021: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-022: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-023: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-024: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-025: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-026: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-027: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-028: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-029: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-030: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-031: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-032: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-033: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-034: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-035: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-036: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-037: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-038: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-039: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-040: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-041: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-042: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-043: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-044: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-045: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-046: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-047: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-048: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-049: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-050: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-051: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-052: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-053: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-054: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-055: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-056: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-057: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-058: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-059: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-060: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-061: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-062: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-063: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-064: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-065: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-066: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-067: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-068: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-069: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-070: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-071: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-072: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-073: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-074: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-075: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-076: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-077: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-078: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-079: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-080: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-081: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-082: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-083: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-084: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-085: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-086: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-087: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-088: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-089: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-090: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```

## MVC-H-091: missing @RequestBody

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Binding
- Concept: missing @RequestBody
- Symptom: JSON fields arrive as null or binding fails.
- Diagnostic goal: Declare the source of request data explicitly.

### Buggy code

```java
public ResponseEntity<Item> create(Item item) { return ok(item); }
```

### Expected diagnosis

MVC does not know that the object should be decoded from the JSON body.

### Corrected code

```java
public ResponseEntity<Item> create(@Valid @RequestBody Item item) { return ok(item); }
```

### Regression tests

```java
// JSON body binds and invalid fields produce 400.
```

## MVC-H-092: constraints never execute

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Validation
- Concept: constraints never execute
- Symptom: Invalid input is accepted.
- Diagnostic goal: Put @Valid at the controller boundary and handle violations.

### Buggy code

```java
public ResponseEntity<?> create(@RequestBody @Valid Item item) { ... }
```

### Expected diagnosis

The annotation is correct only if the DTO has constraints and validation is on the classpath.

### Corrected code

```java
public ResponseEntity<?> create(@Valid @RequestBody ItemRequest item) { ... }
```

### Regression tests

```java
// Missing required fields return a stable validation error body.
```

## MVC-H-093: always returns 200

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Status codes
- Concept: always returns 200
- Symptom: Clients cannot distinguish creation, absence, and failure.
- Diagnostic goal: Use HTTP status as part of the API contract.

### Buggy code

```java
return ResponseEntity.ok(service.create(request));
```

### Expected diagnosis

Creation should communicate its resource location and status.

### Corrected code

```java
return ResponseEntity.created(uri).body(service.create(request));
```

### Regression tests

```java
// Create returns 201 and Location; validation returns 400.
```

## MVC-H-094: controller catches every exception

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Exception mapping
- Concept: controller catches every exception
- Symptom: Errors are duplicated and stack traces leak.
- Diagnostic goal: Centralize mapping with a narrow exception handler.

### Buggy code

```java
try { return ok(service.get(id)); } catch (Exception e) { return badRequest().body(e.getMessage()); }
```

### Expected diagnosis

The controller turns server faults into 400 and exposes internal messages.

### Corrected code

```java
@RestControllerAdvice
class ApiErrors { @ExceptionHandler(NotFoundException.class) ResponseEntity<?> missing() { return ResponseEntity.notFound().build(); } }
```

### Regression tests

```java
// Missing maps to 404; unexpected errors map to 500 without details.
```

## MVC-H-095: wrong media type

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Content negotiation
- Concept: wrong media type
- Symptom: A client receives HTML or a 406 response.
- Diagnostic goal: Declare supported request and response media types.

### Buggy code

```java
@PostMapping("/items") Item create(@RequestBody Item item) { ... }
```

### Expected diagnosis

The endpoint contract does not state which representations it accepts or produces.

### Corrected code

```java
@PostMapping(value="/items", consumes="application/json", produces="application/json") Item create(@RequestBody Item item) { ... }
```

### Regression tests

```java
// JSON requests receive JSON responses and unsupported media types are rejected.
```

## MVC-H-096: wildcard with credentials

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: CORS
- Concept: wildcard with credentials
- Symptom: Browser requests fail or trust too many origins.
- Diagnostic goal: Use an explicit origin policy for credentialed APIs.

### Buggy code

```java
@CrossOrigin(origins="*", allowCredentials="true")
```

### Expected diagnosis

Browsers disallow wildcard origins with credentials and a broad trust policy is unsafe.

### Corrected code

```java
@CrossOrigin(origins="https://app.example", allowCredentials="true")
```

### Regression tests

```java
// The configured origin is allowed and an unrelated origin is rejected.
```

## MVC-H-097: entity exposed directly

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: DTO boundaries
- Concept: entity exposed directly
- Symptom: Internal fields and lazy relationships leak.
- Diagnostic goal: Use request and response DTOs.

### Buggy code

```java
return repository.findById(id).orElseThrow();
```

### Expected diagnosis

Entities couple persistence and wire contracts and may serialize fields unintentionally.

### Corrected code

```java
return mapper.toResponse(repository.findById(id).orElseThrow());
```

### Regression tests

```java
// Response JSON contains only documented fields.
```

## MVC-H-098: retry creates duplicates

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Idempotency
- Concept: retry creates duplicates
- Symptom: A client retry creates two payments.
- Diagnostic goal: Use an idempotency key and a unique persistence constraint.

### Buggy code

```java
@PostMapping("/payments") Payment pay(@RequestBody PaymentRequest request) { return service.pay(request); }
```

### Expected diagnosis

Network retries can repeat a non-idempotent operation.

### Corrected code

```java
@PostMapping("/payments") Payment pay(@RequestHeader("Idempotency-Key") String key, @RequestBody PaymentRequest request) { return service.payOnce(key, request); }
```

### Regression tests

```java
// Repeating the same key returns the original result.
```

## MVC-H-099: large file buffered

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Streaming
- Concept: large file buffered
- Symptom: Memory spikes while downloading a file.
- Diagnostic goal: Stream content through a resource response.

### Buggy code

```java
byte[] data = Files.readAllBytes(path);
return ResponseEntity.ok(data);
```

### Expected diagnosis

Reading the entire file into a byte array scales memory with file size.

### Corrected code

```java
return ResponseEntity.ok().body(new InputStreamResource(Files.newInputStream(path)));
```

### Regression tests

```java
// Large responses keep bounded application memory.
```

## MVC-H-100: user path traversal

- Difficulty: Hard
- Framework: Spring MVC & Web APIs
- Language: Java
- Perspective: Path security
- Concept: user path traversal
- Symptom: A request reads files outside the intended directory.
- Diagnostic goal: Normalize and enforce a resolved path under the allowed root.

### Buggy code

```java
return Files.readString(root.resolve(name));
```

### Expected diagnosis

A name containing ../ can escape root.

### Corrected code

```java
Path target = root.resolve(name).normalize();
if (!target.startsWith(root)) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);
return Files.readString(target);
```

### Regression tests

```java
// Traversal attempts are rejected.
```
