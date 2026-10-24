# Laravel Debug Exercises

A RAG-training corpus of 300 debugging exercises for Laravel. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: types, state, resources, security, persistence, routing, concurrency, errors, testing, and deployment

## LARAVEL-E-001: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-002: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-003: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-004: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-005: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-006: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-007: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-008: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-009: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-010: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-011: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-012: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-013: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-014: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-015: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-016: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-017: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-018: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-019: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-020: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-021: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-022: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-023: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-024: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-025: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-026: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-027: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-028: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-029: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-030: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-031: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-032: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-033: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-034: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-035: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-036: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-037: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-038: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-039: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-040: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-041: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-042: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-043: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-044: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-045: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-046: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-047: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-048: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-049: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-050: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-051: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-052: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-053: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-054: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-055: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-056: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-057: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-058: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-059: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-060: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-061: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-062: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-063: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-064: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-065: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-066: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-067: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-068: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-069: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-070: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-071: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-072: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-073: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-074: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-075: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-076: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-077: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-078: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-079: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-080: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-081: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-082: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-083: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-084: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-085: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-086: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-087: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-088: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-089: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-090: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-E-091: route order shadowing

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-E-092: validated data ignored

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-E-093: N+1 relation

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-E-094: partial write

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-E-095: non-idempotent retry

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-E-096: authorization after work

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-E-097: protection disabled

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-E-098: stale user response

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-E-099: event before commit

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-E-100: raw output

- Difficulty: Easy
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-001: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-002: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-003: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-004: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-005: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-006: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-007: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-008: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-009: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-010: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-011: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-012: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-013: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-014: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-015: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-016: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-017: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-018: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-019: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-020: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-021: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-022: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-023: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-024: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-025: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-026: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-027: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-028: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-029: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-030: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-031: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-032: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-033: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-034: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-035: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-036: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-037: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-038: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-039: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-040: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-041: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-042: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-043: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-044: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-045: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-046: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-047: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-048: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-049: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-050: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-051: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-052: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-053: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-054: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-055: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-056: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-057: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-058: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-059: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-060: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-061: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-062: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-063: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-064: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-065: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-066: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-067: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-068: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-069: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-070: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-071: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-072: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-073: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-074: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-075: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-076: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-077: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-078: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-079: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-080: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-081: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-082: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-083: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-084: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-085: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-086: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-087: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-088: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-089: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-090: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-M-091: route order shadowing

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-M-092: validated data ignored

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-M-093: N+1 relation

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-M-094: partial write

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-M-095: non-idempotent retry

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-M-096: authorization after work

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-M-097: protection disabled

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-M-098: stale user response

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-M-099: event before commit

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-M-100: raw output

- Difficulty: Medium
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-001: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-002: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-003: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-004: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-005: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-006: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-007: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-008: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-009: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-010: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-011: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-012: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-013: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-014: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-015: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-016: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-017: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-018: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-019: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-020: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-021: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-022: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-023: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-024: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-025: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-026: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-027: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-028: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-029: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-030: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-031: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-032: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-033: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-034: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-035: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-036: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-037: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-038: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-039: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-040: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-041: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-042: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-043: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-044: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-045: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-046: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-047: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-048: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-049: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-050: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-051: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-052: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-053: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-054: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-055: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-056: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-057: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-058: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-059: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-060: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-061: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-062: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-063: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-064: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-065: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-066: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-067: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-068: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-069: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-070: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-071: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-072: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-073: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-074: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-075: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-076: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-077: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-078: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-079: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-080: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-081: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-082: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-083: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-084: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-085: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-086: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-087: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-088: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-089: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-090: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```

## LARAVEL-H-091: route order shadowing

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended endpoint is never reached.
- Diagnostic goal: Place specific routes before dynamic catch-alls.

### Buggy code

```php
Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);
```

### Expected diagnosis

The dynamic route captures /admin first.

### Corrected code

```php
Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);
```

### Regression tests

```php
assertRouteIs("/admin", "AdminController@index");
```

## LARAVEL-H-092: validated data ignored

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Validation
- Concept: validated data ignored
- Symptom: Unvalidated request fields reach the model.
- Diagnostic goal: Use the validated payload as the only write input.

### Buggy code

```php
$data = $request->all(); User::create($data);
```

### Expected diagnosis

Calling validate but writing all request fields defeats the boundary.

### Corrected code

```php
$data = $request->validate(["name" => "required|string"]); User::create($data);
```

### Regression tests

```php
assertUnknownFieldIsNotPersisted();
```

## LARAVEL-H-093: N+1 relation

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Eloquent
- Concept: N+1 relation
- Symptom: A list endpoint issues one query per row.
- Diagnostic goal: Eager-load relations used by the response.

### Buggy code

```php
$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;
```

### Expected diagnosis

Lazy relation access performs an extra query for each post.

### Corrected code

```php
$posts = Post::with("author")->get();
```

### Regression tests

```php
assertQueryCountDoesNotGrowPerPost();
```

## LARAVEL-H-094: partial write

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Transactions
- Concept: partial write
- Symptom: A failed checkout leaves an order without payment state.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```php
$order->save(); $payment->save(); $inventory->decrement("stock");
```

### Expected diagnosis

An exception after the first write can commit inconsistent state.

### Corrected code

```php
DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });
```

### Regression tests

```php
assertFailedCheckoutRollsBackAllWrites();
```

## LARAVEL-H-095: non-idempotent retry

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Queues
- Concept: non-idempotent retry
- Symptom: A retried job sends duplicate effects.
- Diagnostic goal: Use a stable idempotency key or unique job.

### Buggy code

```php
public function handle() { Mail::to($this->email)->send(new Receipt); }
```

### Expected diagnosis

Queue retries can run handle more than once.

### Corrected code

```php
public function uniqueId(): string { return (string) $this->orderId; }
```

### Regression tests

```php
assertRetryDoesNotDuplicateReceipt();
```

## LARAVEL-H-096: authorization after work

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Middleware
- Concept: authorization after work
- Symptom: Unauthorized users still trigger expensive work.
- Diagnostic goal: Authorize before loading or mutating protected resources.

### Buggy code

```php
$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);
```

### Expected diagnosis

The controller performs the lookup and may leak timing or data before authorization.

### Corrected code

```php
Gate::authorize("view", $report); return $report;
```

### Regression tests

```php
assertUnauthorizedRequestDoesNotReturnReport();
```

## LARAVEL-H-097: protection disabled

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: CSRF
- Concept: protection disabled
- Symptom: Browser mutations accept cross-site requests.
- Diagnostic goal: Keep CSRF middleware for cookie-authenticated routes.

### Buggy code

```php
$middleware->except(["/profile/update"]);
```

### Expected diagnosis

Excluding a state-changing route removes the browser forgery boundary.

### Corrected code

```php
Route::post("/profile/update", ...);
```

### Regression tests

```php
assertPostWithoutCsrfIsRejected();
```

## LARAVEL-H-098: stale user response

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Caching
- Concept: stale user response
- Symptom: One user sees another user’s cached data.
- Diagnostic goal: Include identity and model version in the key.

### Buggy code

```php
return Cache::remember("profile", 60, fn() => $request->user()->profile);
```

### Expected diagnosis

A global key is shared across users.

### Corrected code

```php
return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);
```

### Regression tests

```php
assertCacheKeyVariesByUser();
```

## LARAVEL-H-099: event before commit

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Events
- Concept: event before commit
- Symptom: A listener observes data that later rolls back.
- Diagnostic goal: Dispatch after a successful transaction commit when required.

### Buggy code

```php
event(new OrderCreated($order)); DB::commit();
```

### Expected diagnosis

The event is published before the transaction outcome is known.

### Corrected code

```php
OrderCreated::dispatch($order)->afterCommit();
```

### Regression tests

```php
assertListenerRunsOnlyAfterCommit();
```

## LARAVEL-H-100: raw output

- Difficulty: Hard
- Language/framework: Laravel
- Perspective: Views
- Concept: raw output
- Symptom: User content renders as executable HTML.
- Diagnostic goal: Use escaped Blade output or sanitize explicitly.

### Buggy code

```php
{!! $comment->body !!}
```

### Expected diagnosis

The raw Blade tag bypasses HTML escaping.

### Corrected code

```php
{{ $comment->body }}
```

### Regression tests

```php
assertScriptMarkupIsEscaped();
```
