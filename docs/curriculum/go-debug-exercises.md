# Go Debug Exercises

A RAG-training corpus of 300 debugging exercises for Go. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, state, memory/ownership, concurrency, errors, APIs, security, persistence, and testing

## GO-E-001: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-002: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-003: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-004: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-005: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-006: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-007: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-008: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-009: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-010: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-011: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-012: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-013: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-014: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-015: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-016: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-017: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-018: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-019: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-020: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-021: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-022: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-023: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-024: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-025: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-026: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-027: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-028: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-029: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-030: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-031: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-032: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-033: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-034: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-035: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-036: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-037: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-038: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-039: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-040: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-041: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-042: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-043: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-044: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-045: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-046: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-047: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-048: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-049: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-050: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-051: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-052: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-053: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-054: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-055: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-056: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-057: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-058: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-059: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-060: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-061: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-062: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-063: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-064: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-065: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-066: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-067: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-068: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-069: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-070: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-071: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-072: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-073: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-074: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-075: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-076: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-077: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-078: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-079: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-080: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-081: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-082: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-083: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-084: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-085: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-086: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-087: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-088: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-089: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-090: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-E-091: typed nil interface

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-E-092: ignored error

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-E-093: goroutine leak

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-E-094: close send panic

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-E-095: context ignored

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-E-096: body not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-E-097: concurrent map write

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-E-098: append aliasing

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-E-099: unknown fields accepted

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-E-100: rows not closed

- Difficulty: Easy
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-001: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-002: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-003: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-004: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-005: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-006: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-007: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-008: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-009: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-010: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-011: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-012: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-013: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-014: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-015: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-016: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-017: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-018: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-019: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-020: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-021: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-022: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-023: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-024: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-025: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-026: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-027: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-028: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-029: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-030: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-031: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-032: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-033: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-034: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-035: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-036: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-037: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-038: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-039: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-040: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-041: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-042: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-043: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-044: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-045: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-046: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-047: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-048: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-049: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-050: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-051: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-052: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-053: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-054: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-055: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-056: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-057: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-058: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-059: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-060: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-061: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-062: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-063: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-064: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-065: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-066: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-067: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-068: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-069: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-070: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-071: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-072: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-073: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-074: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-075: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-076: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-077: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-078: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-079: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-080: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-081: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-082: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-083: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-084: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-085: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-086: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-087: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-088: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-089: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-090: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-M-091: typed nil interface

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-M-092: ignored error

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-M-093: goroutine leak

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-M-094: close send panic

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-M-095: context ignored

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-M-096: body not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-M-097: concurrent map write

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-M-098: append aliasing

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-M-099: unknown fields accepted

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-M-100: rows not closed

- Difficulty: Medium
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-001: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-002: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-003: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-004: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-005: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-006: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-007: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-008: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-009: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-010: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-011: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-012: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-013: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-014: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-015: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-016: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-017: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-018: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-019: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-020: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-021: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-022: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-023: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-024: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-025: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-026: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-027: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-028: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-029: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-030: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-031: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-032: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-033: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-034: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-035: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-036: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-037: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-038: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-039: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-040: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-041: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-042: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-043: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-044: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-045: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-046: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-047: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-048: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-049: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-050: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-051: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-052: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-053: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-054: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-055: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-056: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-057: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-058: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-059: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-060: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-061: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-062: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-063: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-064: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-065: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-066: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-067: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-068: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-069: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-070: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-071: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-072: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-073: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-074: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-075: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-076: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-077: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-078: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-079: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-080: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-081: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-082: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-083: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-084: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-085: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-086: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-087: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-088: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-089: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-090: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```

## GO-H-091: typed nil interface

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Nil interfaces
- Concept: typed nil interface
- Symptom: A nil check passes and a method panics.
- Diagnostic goal: Understand the dynamic type/value pair in an interface.

### Buggy code

```go
var p *Profile = nil
var value any = p
if value != nil { value.(*Profile).Name }
```

### Expected diagnosis

An interface containing a typed nil pointer is itself non-nil.

### Corrected code

```go
if p != nil { var value any = p; use(value) }
```

### Regression tests

```go
assert_no_panic_for_nil_profile()
```

## GO-H-092: ignored error

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Errors
- Concept: ignored error
- Symptom: The program uses an invalid zero value.
- Diagnostic goal: Handle errors immediately and preserve context.

### Buggy code

```go
data, _ := os.ReadFile(path)
return parse(data)
```

### Expected diagnosis

Ignoring an I/O error makes the following parse operate on incomplete or nil data.

### Corrected code

```go
data, err := os.ReadFile(path)
if err != nil { return err }
return parse(data)
```

### Regression tests

```go
assert_error_is_returned_for_missing_file()
```

## GO-H-093: goroutine leak

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Goroutines
- Concept: goroutine leak
- Symptom: Memory and scheduler work grow after requests finish.
- Diagnostic goal: Give goroutines cancellation and ensure every send/receive can exit.

### Buggy code

```go
go func() { result <- fetch() }()
```

### Expected diagnosis

A receiver that returns early leaves the sender blocked forever.

### Corrected code

```go
go func() { select { case result <- fetch(): case <-ctx.Done(): } }()
```

### Regression tests

```go
assert_goroutine_count_returns_to_baseline()
```

## GO-H-094: close send panic

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Channels
- Concept: close send panic
- Symptom: A worker panics while reporting completion.
- Diagnostic goal: Define one owner responsible for closing a channel.

### Buggy code

```go
for _, worker := range workers { go worker(out); go close(out) }
```

### Expected diagnosis

Multiple goroutines can close the same channel or close before sends complete.

### Corrected code

```go
go func() { wg.Wait(); close(out) }()
```

### Regression tests

```go
assert_all_results_received_without_panic()
```

## GO-H-095: context ignored

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Context
- Concept: context ignored
- Symptom: Canceled requests continue doing work.
- Diagnostic goal: Pass context through every blocking dependency.

### Buggy code

```go
func Load(ctx context.Context) (Data, error) { return client.Get() }
```

### Expected diagnosis

The dependency cannot observe cancellation when ctx is not passed.

### Corrected code

```go
func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }
```

### Regression tests

```go
assert_cancel_stops_upstream_call()
```

## GO-H-096: body not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: HTTP
- Concept: body not closed
- Symptom: Connections are not reused and resources leak.
- Diagnostic goal: Close response bodies on every successful response.

### Buggy code

```go
resp, err := http.Get(url)
if err != nil { return err }
return decode(resp.Body)
```

### Expected diagnosis

The response body remains open after decoding.

### Corrected code

```go
resp, err := http.Get(url)
if err != nil { return err }
defer resp.Body.Close()
return decode(resp.Body)
```

### Regression tests

```go
assert_body_closed_after_request()
```

## GO-H-097: concurrent map write

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Maps
- Concept: concurrent map write
- Symptom: The runtime reports fatal concurrent map writes.
- Diagnostic goal: Protect maps or use a concurrency-safe design.

### Buggy code

```go
counts[key]++
```

### Expected diagnosis

A map is not safe for concurrent writes, and the increment is a compound operation.

### Corrected code

```go
mu.Lock()
counts[key]++
mu.Unlock()
```

### Regression tests

```go
go run -race reports no race
```

## GO-H-098: append aliasing

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Slices
- Concept: append aliasing
- Symptom: A caller sees unexpected mutation.
- Diagnostic goal: Copy before retaining or returning a slice with independent ownership.

### Buggy code

```go
func keep(values []byte) []byte { return values[:3] }
```

### Expected diagnosis

The returned slice aliases the caller’s backing array.

### Corrected code

```go
func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }
```

### Regression tests

```go
assert_mutating_input_does_not_change_result()
```

## GO-H-099: unknown fields accepted

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: JSON
- Concept: unknown fields accepted
- Symptom: Clients send misspelled fields that are silently ignored.
- Diagnostic goal: Configure strict decoding at the input boundary.

### Buggy code

```go
json.NewDecoder(r.Body).Decode(&request)
```

### Expected diagnosis

The default decoder ignores unknown JSON keys, hiding client contract errors.

### Corrected code

```go
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
err := decoder.Decode(&request)
```

### Regression tests

```go
assert_unknown_field_returns_400()
```

## GO-H-100: rows not closed

- Difficulty: Hard
- Language/framework: Go / Go
- Perspective: Database
- Concept: rows not closed
- Symptom: Connection pool exhaustion appears under load.
- Diagnostic goal: Close rows and check iteration errors.

### Buggy code

```go
rows, err := db.QueryContext(ctx, query)
for rows.Next() { scan(rows) }
```

### Expected diagnosis

Rows hold a pooled connection until closed and may report errors after iteration.

### Corrected code

```go
rows, err := db.QueryContext(ctx, query)
if err != nil { return err }
defer rows.Close()
for rows.Next() { scan(rows) }
return rows.Err()
```

### Regression tests

```go
assert_rows_closed_and_iteration_error_returned()
```
