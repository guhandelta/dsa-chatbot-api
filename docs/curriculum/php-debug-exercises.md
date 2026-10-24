# PHP Debug Exercises

A RAG-training corpus of 300 debugging exercises for PHP. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: types, state, resources, security, persistence, routing, concurrency, errors, testing, and deployment

## PHP-E-001: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-002: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-003: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-004: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-005: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-006: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-007: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-008: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-009: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-010: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-011: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-012: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-013: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-014: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-015: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-016: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-017: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-018: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-019: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-020: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-021: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-022: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-023: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-024: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-025: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-026: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-027: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-028: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-029: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-030: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-031: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-032: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-033: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-034: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-035: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-036: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-037: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-038: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-039: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-040: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-041: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-042: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-043: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-044: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-045: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-046: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-047: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-048: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-049: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-050: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-051: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-052: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-053: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-054: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-055: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-056: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-057: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-058: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-059: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-060: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-061: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-062: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-063: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-064: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-065: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-066: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-067: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-068: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-069: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-070: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-071: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-072: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-073: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-074: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-075: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-076: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-077: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-078: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-079: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-080: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-081: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-082: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-083: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-084: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-085: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-086: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-087: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-088: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-089: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-090: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-E-091: loose comparison

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-E-092: missing key warning

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-E-093: unexpected alias

- Difficulty: Easy
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-E-094: return contract mismatch

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-E-095: catching Throwable broadly

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-E-096: file handle leak

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-E-097: unsafe SQL interpolation

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-E-098: json error ignored

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-E-099: missing regeneration

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-E-100: wrong imported symbol

- Difficulty: Easy
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-001: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-002: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-003: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-004: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-005: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-006: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-007: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-008: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-009: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-010: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-011: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-012: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-013: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-014: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-015: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-016: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-017: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-018: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-019: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-020: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-021: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-022: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-023: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-024: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-025: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-026: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-027: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-028: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-029: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-030: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-031: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-032: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-033: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-034: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-035: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-036: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-037: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-038: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-039: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-040: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-041: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-042: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-043: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-044: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-045: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-046: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-047: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-048: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-049: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-050: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-051: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-052: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-053: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-054: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-055: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-056: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-057: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-058: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-059: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-060: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-061: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-062: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-063: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-064: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-065: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-066: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-067: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-068: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-069: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-070: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-071: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-072: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-073: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-074: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-075: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-076: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-077: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-078: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-079: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-080: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-081: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-082: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-083: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-084: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-085: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-086: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-087: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-088: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-089: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-090: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-M-091: loose comparison

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-M-092: missing key warning

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-M-093: unexpected alias

- Difficulty: Medium
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-M-094: return contract mismatch

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-M-095: catching Throwable broadly

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-M-096: file handle leak

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-M-097: unsafe SQL interpolation

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-M-098: json error ignored

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-M-099: missing regeneration

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-M-100: wrong imported symbol

- Difficulty: Medium
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-001: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-002: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-003: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-004: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-005: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-006: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-007: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-008: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-009: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-010: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-011: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-012: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-013: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-014: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-015: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-016: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-017: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-018: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-019: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-020: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-021: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-022: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-023: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-024: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-025: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-026: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-027: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-028: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-029: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-030: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-031: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-032: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-033: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-034: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-035: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-036: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-037: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-038: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-039: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-040: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-041: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-042: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-043: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-044: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-045: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-046: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-047: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-048: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-049: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-050: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-051: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-052: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-053: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-054: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-055: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-056: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-057: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-058: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-059: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-060: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-061: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-062: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-063: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-064: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-065: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-066: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-067: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-068: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-069: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-070: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-071: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-072: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-073: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-074: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-075: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-076: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-077: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-078: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-079: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-080: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-081: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-082: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-083: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-084: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-085: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-086: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-087: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-088: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-089: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-090: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```

## PHP-H-091: loose comparison

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Types
- Concept: loose comparison
- Symptom: An invalid value passes validation.
- Diagnostic goal: Use strict comparison and explicit input normalization.

### Buggy code

```php
if ($value == 0) { accept(); }
```

### Expected diagnosis

PHP type juggling makes strings, false, and zero compare equal in surprising cases.

### Corrected code

```php
if (is_int($value) && $value === 0) { accept(); }
```

### Regression tests

```php
assert(reject("0")); assert(accept(0));
```

## PHP-H-092: missing key warning

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Arrays
- Concept: missing key warning
- Symptom: A request emits warnings or uses the wrong default.
- Diagnostic goal: Check presence separately from truthiness.

### Buggy code

```php
$limit = $options["limit"] ?: 10;
```

### Expected diagnosis

The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.

### Corrected code

```php
$limit = $options["limit"] ?? 10;
```

### Regression tests

```php
assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);
```

## PHP-H-093: unexpected alias

- Difficulty: Hard
- Language/framework: PHP
- Perspective: References
- Concept: unexpected alias
- Symptom: Changing one variable changes another.
- Diagnostic goal: Unset references after use and avoid accidental aliasing.

### Buggy code

```php
$a = 1; $b =& $a; $b = 2;
```

### Expected diagnosis

The reference makes both variables aliases of the same storage.

### Corrected code

```php
$a = 1; $b = $a; $b = 2;
```

### Regression tests

```php
assert($a === 1); assert($b === 2);
```

## PHP-H-094: return contract mismatch

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Functions
- Concept: return contract mismatch
- Symptom: The caller receives null instead of the computed value.
- Diagnostic goal: Return on every path and declare the return type.

### Buggy code

```php
function total(array $items): int { foreach ($items as $item) { $sum += $item; } }
```

### Expected diagnosis

The accumulator is uninitialized and the function has no return statement.

### Corrected code

```php
function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }
```

### Regression tests

```php
assert(total([1,2,3]) === 6);
```

## PHP-H-095: catching Throwable broadly

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Exceptions
- Concept: catching Throwable broadly
- Symptom: A programming error becomes a normal response.
- Diagnostic goal: Catch expected exceptions and log unexpected failures.

### Buggy code

```php
try { process($input); } catch (Throwable $e) { return null; }
```

### Expected diagnosis

Catching every Throwable hides bugs and can swallow engine errors.

### Corrected code

```php
try { process($input); } catch (InvalidArgumentException $e) { return null; }
```

### Regression tests

```php
assertThrowsForProgrammerError();
```

## PHP-H-096: file handle leak

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Resources
- Concept: file handle leak
- Symptom: Repeated calls exhaust descriptors.
- Diagnostic goal: Use finally or a scoped helper to close resources.

### Buggy code

```php
$handle = fopen($path, "rb"); return fread($handle, 100);
```

### Expected diagnosis

An exception or early return can skip fclose.

### Corrected code

```php
$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }
```

### Regression tests

```php
assertHandleClosedAfterSuccessAndFailure();
```

## PHP-H-097: unsafe SQL interpolation

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Security
- Concept: unsafe SQL interpolation
- Symptom: Input changes the query predicate.
- Diagnostic goal: Use parameterized queries.

### Buggy code

```php
$pdo->query("SELECT * FROM users WHERE id = $id");
```

### Expected diagnosis

Interpolating untrusted input permits SQL injection.

### Corrected code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);
```

### Regression tests

```php
assertInjectionPayloadCannotAlterPredicate();
```

## PHP-H-098: json error ignored

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Serialization
- Concept: json error ignored
- Symptom: Invalid JSON becomes null data.
- Diagnostic goal: Check decoding errors explicitly.

### Buggy code

```php
$data = json_decode($body, true); return $data["name"];
```

### Expected diagnosis

json_decode returns null for invalid JSON unless the caller requests exceptions.

### Corrected code

```php
$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];
```

### Regression tests

```php
assertThrowsOnMalformedJson();
```

## PHP-H-099: missing regeneration

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Sessions
- Concept: missing regeneration
- Symptom: Login remains vulnerable to fixation.
- Diagnostic goal: Regenerate the session identifier after authentication.

### Buggy code

```php
$_SESSION["user_id"] = $user->id;
```

### Expected diagnosis

Keeping the pre-authentication identifier permits session fixation.

### Corrected code

```php
session_regenerate_id(true); $_SESSION["user_id"] = $user->id;
```

### Regression tests

```php
assertSessionIdChangesAfterLogin();
```

## PHP-H-100: wrong imported symbol

- Difficulty: Hard
- Language/framework: PHP
- Perspective: Namespaces
- Concept: wrong imported symbol
- Symptom: The class is not found in production.
- Diagnostic goal: Use the declared namespace and import the exact class.

### Buggy code

```php
use App\User; $user = new Users();
```

### Expected diagnosis

The imported symbol and constructed class name differ.

### Corrected code

```php
use App\User; $user = new User();
```

### Regression tests

```php
assertClassResolvesWithoutFallback();
```
