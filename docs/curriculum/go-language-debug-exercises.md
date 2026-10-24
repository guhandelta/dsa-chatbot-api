# Go Debug Exercises

A RAG-training corpus of 300 debugging exercises for Go. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory, ownership, concurrency, timing, APIs, errors, security, persistence, and testing

## GO-E-001: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-002: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-003: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-004: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-005: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-006: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-007: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-008: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-009: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-010: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-011: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-012: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-013: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-014: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-015: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-016: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-017: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-018: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-019: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-020: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-021: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-022: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-023: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-024: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-025: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-026: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-027: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-028: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-029: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-030: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-031: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-032: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-033: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-034: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-035: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-036: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-037: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-038: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-039: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-040: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-041: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-042: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-043: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-044: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-045: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-046: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-047: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-048: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-049: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-050: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-051: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-052: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-053: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-054: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-055: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-056: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-057: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-058: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-059: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-060: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-061: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-062: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-063: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-064: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-065: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-066: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-067: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-068: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-069: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-070: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-071: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-072: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-073: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-074: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-075: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-076: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-077: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-078: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-079: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-080: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-081: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-082: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-083: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-084: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-085: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-086: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-087: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-088: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-089: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-090: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-E-091: ignored error

- Difficulty: Easy
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-E-092: leaked sender

- Difficulty: Easy
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-E-093: multiple close

- Difficulty: Easy
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-E-094: ignored cancellation

- Difficulty: Easy
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-E-095: concurrent write

- Difficulty: Easy
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-E-096: body not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-E-097: unknown fields ignored

- Difficulty: Easy
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-098: backing array alias

- Difficulty: Easy
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-E-099: rows not closed

- Difficulty: Easy
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-E-100: typed nil

- Difficulty: Easy
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-001: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-002: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-003: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-004: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-005: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-006: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-007: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-008: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-009: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-010: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-011: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-012: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-013: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-014: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-015: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-016: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-017: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-018: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-019: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-020: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-021: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-022: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-023: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-024: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-025: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-026: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-027: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-028: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-029: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-030: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-031: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-032: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-033: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-034: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-035: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-036: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-037: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-038: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-039: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-040: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-041: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-042: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-043: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-044: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-045: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-046: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-047: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-048: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-049: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-050: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-051: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-052: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-053: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-054: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-055: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-056: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-057: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-058: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-059: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-060: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-061: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-062: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-063: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-064: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-065: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-066: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-067: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-068: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-069: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-070: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-071: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-072: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-073: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-074: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-075: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-076: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-077: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-078: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-079: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-080: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-081: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-082: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-083: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-084: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-085: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-086: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-087: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-088: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-089: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-090: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-M-091: ignored error

- Difficulty: Medium
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-M-092: leaked sender

- Difficulty: Medium
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-M-093: multiple close

- Difficulty: Medium
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-M-094: ignored cancellation

- Difficulty: Medium
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-M-095: concurrent write

- Difficulty: Medium
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-M-096: body not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-M-097: unknown fields ignored

- Difficulty: Medium
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-098: backing array alias

- Difficulty: Medium
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-M-099: rows not closed

- Difficulty: Medium
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-M-100: typed nil

- Difficulty: Medium
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-001: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-002: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-003: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-004: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-005: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-006: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-007: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-008: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-009: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-010: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-011: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-012: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-013: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-014: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-015: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-016: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-017: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-018: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-019: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-020: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-021: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-022: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-023: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-024: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-025: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-026: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-027: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-028: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-029: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-030: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-031: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-032: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-033: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-034: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-035: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-036: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-037: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-038: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-039: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-040: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-041: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-042: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-043: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-044: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-045: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-046: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-047: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-048: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-049: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-050: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-051: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-052: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-053: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-054: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-055: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-056: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-057: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-058: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-059: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-060: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-061: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-062: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-063: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-064: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-065: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-066: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-067: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-068: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-069: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-070: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-071: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-072: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-073: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-074: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-075: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-076: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-077: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-078: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-079: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-080: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-081: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-082: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-083: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-084: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-085: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-086: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-087: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-088: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-089: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-090: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```

## GO-H-091: ignored error

- Difficulty: Hard
- Language/platform: Go
- Perspective: Errors
- Concept: ignored error
- Symptom: Invalid data reaches business logic.
- Diagnostic goal: Handle and wrap errors immediately.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring I/O failure makes later behavior misleading.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_missing_file_returns_error()
```

## GO-H-092: leaked sender

- Difficulty: Hard
- Language/platform: Go
- Perspective: Goroutines
- Concept: leaked sender
- Symptom: A request leaves background goroutines blocked.
- Diagnostic goal: Select on cancellation at every blocking operation.

### Buggy code

```go
go func() { results <- work() }()
```

### Expected diagnosis

If the receiver returns early, the send blocks forever.

### Corrected code

```go
go func() { select { case results <- work(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutines_return_to_baseline()
```

## GO-H-093: multiple close

- Difficulty: Hard
- Language/platform: Go
- Perspective: Channels
- Concept: multiple close
- Symptom: A worker panics with close of closed channel.
- Diagnostic goal: Let one coordinator own channel closure.

### Buggy code

```go
for range workers { go func() { close(out) }() }
```

### Expected diagnosis

Multiple workers can close the same channel.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_results_close_once()
```

## GO-H-094: ignored cancellation

- Difficulty: Hard
- Language/platform: Go
- Perspective: Context
- Concept: ignored cancellation
- Symptom: Canceled HTTP requests continue consuming resources.
- Diagnostic goal: Pass context to every dependency.

### Buggy code

```go
func Load(ctx context.Context) error { _, err := client.Get(url); return err }
```

### Expected diagnosis

The HTTP request has no cancellation path.

### Corrected code

```go
func Load(ctx context.Context) error { req, _ := http.NewRequestWithContext(ctx, http.MethodGet, url, nil); _, err := client.Do(req); return err }
```

### Regression tests

```go
assert_cancel_aborts_request()
```

## GO-H-095: concurrent write

- Difficulty: Hard
- Language/platform: Go
- Perspective: Maps
- Concept: concurrent write
- Symptom: The runtime reports concurrent map writes.
- Diagnostic goal: Guard compound map updates.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map and its read-modify-write operation are not safe concurrently.

### Corrected code

```go
mu.Lock(); counts[key]++; mu.Unlock()
```

### Regression tests

```go
go test -race reports no race
```

## GO-H-096: body not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections and file descriptors leak.
- Diagnostic goal: Close response bodies on all successful responses.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The body owns a reusable connection until closed.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed()
```

## GO-H-097: unknown fields ignored

- Difficulty: Hard
- Language/platform: Go
- Perspective: JSON
- Concept: unknown fields ignored
- Symptom: Misspelled client fields silently disappear.
- Diagnostic goal: Use strict decoding at the API boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder accepts unknown keys.

### Corrected code

```go
decoder := json.NewDecoder(r.Body); decoder.DisallowUnknownFields(); err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-098: backing array alias

- Difficulty: Hard
- Language/platform: Go
- Perspective: Slices
- Concept: backing array alias
- Symptom: A retained result changes when input is reused.
- Diagnostic goal: Copy data when ownership must be independent.

### Buggy code

```go
func keep(b []byte) []byte { return b[:3] }
```

### Expected diagnosis

The result aliases the caller backing array.

### Corrected code

```go
func keep(b []byte) []byte { out := make([]byte, 3); copy(out, b[:3]); return out }
```

### Regression tests

```go
assert_input_mutation_does_not_change_result()
```

## GO-H-099: rows not closed

- Difficulty: Hard
- Language/platform: Go
- Perspective: Database
- Concept: rows not closed
- Symptom: The pool exhausts under repeated queries.
- Diagnostic goal: Close rows and return iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, q)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows retain a connection and errors can occur after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, q); if err != nil { return err }; defer rows.Close(); for rows.Next() { scan(rows) }; return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_errors_returned()
```

## GO-H-100: typed nil

- Difficulty: Hard
- Language/platform: Go
- Perspective: Interfaces
- Concept: typed nil
- Symptom: A nil check passes for a nil pointer stored in an interface.
- Diagnostic goal: Check the concrete pointer before boxing or define a nil-safe method.

### Buggy code

```go
var p *Thing; var x any = p; if x != nil { x.(Thing).Run() }
```

### Expected diagnosis

An interface is non-nil when it has a dynamic type even if its pointer value is nil.

### Corrected code

```go
var p *Thing; if p != nil { var x any = p; x.(*Thing).Run() }
```

### Regression tests

```go
assert_typed_nil_is_safe()
```
