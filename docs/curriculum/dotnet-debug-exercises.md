# .NET Debug Exercises

A RAG-training corpus of 300 debugging exercises for .NET. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory and ownership, concurrency, API contracts, persistence, validation, security, lifecycle, testing, and deployment

## NET-E-001: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-002: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-003: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-004: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-005: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-006: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-007: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-008: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-009: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-010: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-011: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-012: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-013: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-014: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-015: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-016: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-017: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-018: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-019: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-020: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-021: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-022: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-023: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-024: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-025: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-026: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-027: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-028: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-029: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-030: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-031: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-032: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-033: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-034: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-035: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-036: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-037: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-038: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-039: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-040: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-041: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-042: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-043: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-044: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-045: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-046: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-047: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-048: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-049: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-050: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-051: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-052: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-053: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-054: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-055: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-056: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-057: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-058: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-059: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-060: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-061: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-062: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-063: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-064: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-065: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-066: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-067: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-068: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-069: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-070: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-071: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-072: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-073: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-074: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-075: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-076: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-077: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-078: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-079: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-080: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-081: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-082: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-083: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-084: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-085: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-086: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-087: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-088: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-089: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-090: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-E-091: wrong service lifetime

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-E-092: ambiguous route

- Difficulty: Easy
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-E-093: short-circuit omission

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-E-094: environment secret in source

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-E-095: reference loop

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-E-096: query executed after context disposal

- Difficulty: Easy
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-E-097: unhandled background exception

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-E-098: new client per request

- Difficulty: Easy
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-E-099: authentication confused with authorization

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-E-100: health endpoint checks no dependency

- Difficulty: Easy
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-001: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-002: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-003: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-004: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-005: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-006: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-007: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-008: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-009: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-010: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-011: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-012: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-013: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-014: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-015: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-016: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-017: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-018: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-019: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-020: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-021: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-022: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-023: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-024: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-025: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-026: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-027: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-028: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-029: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-030: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-031: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-032: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-033: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-034: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-035: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-036: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-037: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-038: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-039: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-040: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-041: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-042: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-043: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-044: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-045: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-046: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-047: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-048: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-049: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-050: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-051: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-052: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-053: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-054: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-055: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-056: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-057: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-058: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-059: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-060: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-061: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-062: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-063: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-064: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-065: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-066: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-067: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-068: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-069: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-070: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-071: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-072: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-073: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-074: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-075: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-076: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-077: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-078: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-079: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-080: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-081: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-082: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-083: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-084: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-085: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-086: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-087: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-088: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-089: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-090: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-M-091: wrong service lifetime

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-M-092: ambiguous route

- Difficulty: Medium
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-M-093: short-circuit omission

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-M-094: environment secret in source

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-M-095: reference loop

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-M-096: query executed after context disposal

- Difficulty: Medium
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-M-097: unhandled background exception

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-M-098: new client per request

- Difficulty: Medium
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-M-099: authentication confused with authorization

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-M-100: health endpoint checks no dependency

- Difficulty: Medium
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-001: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-002: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-003: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-004: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-005: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-006: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-007: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-008: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-009: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-010: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-011: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-012: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-013: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-014: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-015: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-016: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-017: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-018: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-019: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-020: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-021: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-022: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-023: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-024: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-025: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-026: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-027: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-028: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-029: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-030: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-031: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-032: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-033: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-034: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-035: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-036: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-037: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-038: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-039: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-040: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-041: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-042: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-043: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-044: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-045: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-046: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-047: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-048: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-049: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-050: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-051: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-052: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-053: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-054: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-055: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-056: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-057: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-058: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-059: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-060: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-061: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-062: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-063: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-064: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-065: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-066: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-067: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-068: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-069: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-070: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-071: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-072: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-073: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-074: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-075: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-076: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-077: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-078: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-079: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-080: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-081: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-082: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-083: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-084: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-085: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-086: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-087: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-088: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-089: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-090: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```

## NET-H-091: wrong service lifetime

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Dependency injection
- Concept: wrong service lifetime
- Symptom: A scoped dependency is resolved from a singleton.
- Diagnostic goal: Align lifetimes with ownership and request scope.

### Buggy code

```csharp
services.AddSingleton<ReportService1>();
services.AddScoped<DbContext1>();
```

### Expected diagnosis

A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.

### Corrected code

```csharp
services.AddScoped<ReportService1>();
services.AddScoped<DbContext1>();
```

### Regression tests

```csharp
// Provider validation passes and each request gets a scoped report service.
```

## NET-H-092: ambiguous route

- Difficulty: Hard
- Language/platform: .NET
- Perspective: ASP.NET routing
- Concept: ambiguous route
- Symptom: Requests match the wrong action or fail startup.
- Diagnostic goal: Make route templates and constraints unambiguous.

### Buggy code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Expected diagnosis

Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.

### Corrected code

```csharp
[HttpGet("{id}")]
public IActionResult Get(string id) => Ok(id);
[HttpGet("{id:int}")]
public IActionResult GetByNumber(int id) => Ok(id);
```

### Regression tests

```csharp
// Text and integer routes select the intended action.
```

## NET-H-093: short-circuit omission

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Middleware
- Concept: short-circuit omission
- Symptom: A response is written twice or the pipeline continues after a terminal response.
- Diagnostic goal: Return immediately when middleware owns the response.

### Buggy code

```csharp
if (!authorized) { context.Response.StatusCode = 401; }
await next(context);
```

### Expected diagnosis

Unauthorized requests still reach downstream middleware and may overwrite the response.

### Corrected code

```csharp
if (!authorized) { context.Response.StatusCode = 401; return; }
await next(context);
```

### Regression tests

```csharp
// Unauthorized requests never invoke the downstream delegate.
```

## NET-H-094: environment secret in source

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Configuration
- Concept: environment secret in source
- Symptom: Production uses a development credential.
- Diagnostic goal: Load secrets from managed configuration providers.

### Buggy code

```csharp
builder.Configuration["ApiKey"] = "dev-key";
```

### Expected diagnosis

Source-controlled secrets are exposed and override deployment configuration.

### Corrected code

```csharp
var key = builder.Configuration["ApiKey"] ?? throw new InvalidOperationException("ApiKey required");
```

### Regression tests

```csharp
// Startup fails without configured ApiKey and never embeds a secret.
```

## NET-H-095: reference loop

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Serialization
- Concept: reference loop
- Symptom: JSON serialization throws or emits an enormous graph.
- Diagnostic goal: Shape DTOs to the API boundary instead of serializing the entity graph.

### Buggy code

```csharp
return Results.Json(order1);
```

### Expected diagnosis

Bidirectional navigation properties can create cycles and expose persistence details.

### Corrected code

```csharp
return Results.Ok(new OrderDto1(order1.Id, order1.Total));
```

### Regression tests

```csharp
// Response contains only the documented DTO fields.
```

## NET-H-096: query executed after context disposal

- Difficulty: Hard
- Language/platform: .NET
- Perspective: EF Core
- Concept: query executed after context disposal
- Symptom: Enumeration throws ObjectDisposedException.
- Diagnostic goal: Materialize within the context or keep the context alive through enumeration.

### Buggy code

```csharp
IQueryable<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }
```

### Expected diagnosis

IQueryable is deferred; the database access happens after the context is disposed.

### Corrected code

```csharp
IReadOnlyList<Item1> Query1() { using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }
```

### Regression tests

```csharp
// The returned list can be enumerated after Query1 returns.
```

## NET-H-097: unhandled background exception

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Hosted services
- Concept: unhandled background exception
- Symptom: A worker stops silently or takes down the host.
- Diagnostic goal: Observe failures and define restart behavior.

### Buggy code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) await WorkAsync(); }
```

### Expected diagnosis

An exception escapes the loop without logging or a deliberate recovery policy.

### Corrected code

```csharp
protected override async Task ExecuteAsync(CancellationToken token) { while (!token.IsCancellationRequested) { try { await WorkAsync(token); } catch (Exception ex) when (!token.IsCancellationRequested) { logger.LogError(ex, "worker failed"); await Task.Delay(TimeSpan.FromSeconds(1), token); } } }
```

### Regression tests

```csharp
// Transient failure is logged and retried; cancellation exits cleanly.
```

## NET-H-098: new client per request

- Difficulty: Hard
- Language/platform: .NET
- Perspective: HTTP clients
- Concept: new client per request
- Symptom: Sockets exhaust under load.
- Diagnostic goal: Use IHttpClientFactory or a long-lived handler-managed client.

### Buggy code

```csharp
using var client = new HttpClient();
return await client.GetAsync(url);
```

### Expected diagnosis

Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.

### Corrected code

```csharp
return await httpClient.GetAsync(url, token);
```

### Regression tests

```csharp
// The injected client is reused and supports cancellation.
```

## NET-H-099: authentication confused with authorization

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Authorization
- Concept: authentication confused with authorization
- Symptom: Any signed-in user can access an admin operation.
- Diagnostic goal: Require the policy or role for the operation.

### Buggy code

```csharp
[Authorize]
public IActionResult Delete(int id) => Ok();
```

### Expected diagnosis

[Authorize] proves identity but does not require the administrator policy.

### Corrected code

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) => Ok();
```

### Regression tests

```csharp
// Authenticated nonadmins receive 403; admins may delete.
```

## NET-H-100: health endpoint checks no dependency

- Difficulty: Hard
- Language/platform: .NET
- Perspective: Health checks
- Concept: health endpoint checks no dependency
- Symptom: Orchestrator keeps a broken instance in service.
- Diagnostic goal: Separate liveness from readiness and check critical dependencies.

### Buggy code

```csharp
app.MapHealthChecks("/health");
```

### Expected diagnosis

A process-level endpoint can be healthy while its database or queue is unavailable.

### Corrected code

```csharp
app.MapHealthChecks("/ready", new HealthCheckOptions { Predicate = check => check.Tags.Contains("ready") });
```

### Regression tests

```csharp
// Readiness fails when a tagged critical dependency is unavailable.
```
