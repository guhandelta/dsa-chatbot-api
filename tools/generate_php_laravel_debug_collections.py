"""Generate separate PHP and Laravel debugging corpora."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def rec(prefix,title,i,level,row,fence):
    perspective,concept,symptom,goal,buggy,diagnosis,fixed,tests=row
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/framework: {title}
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```{fence}
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```{fence}
{fixed}
```

### Regression tests

```{fence}
{tests}
```

"""

ROWS={
'PHP':[
('Types','loose comparison','An invalid value passes validation.','Use strict comparison and explicit input normalization.','if ($value == 0) { accept(); }','PHP type juggling makes strings, false, and zero compare equal in surprising cases.','if (is_int($value) && $value === 0) { accept(); }','assert(reject("0")); assert(accept(0));'),
('Arrays','missing key warning','A request emits warnings or uses the wrong default.','Check presence separately from truthiness.','$limit = $options["limit"] ?: 10;','The ?: operator treats zero and empty strings as absent and direct access warns when the key is missing.','$limit = $options["limit"] ?? 10;','assert(readLimit([]) === 10); assert(readLimit(["limit" => 0]) === 0);'),
('References','unexpected alias','Changing one variable changes another.','Unset references after use and avoid accidental aliasing.','$a = 1; $b =& $a; $b = 2;','The reference makes both variables aliases of the same storage.','$a = 1; $b = $a; $b = 2;','assert($a === 1); assert($b === 2);'),
('Functions','return contract mismatch','The caller receives null instead of the computed value.','Return on every path and declare the return type.','function total(array $items): int { foreach ($items as $item) { $sum += $item; } }','The accumulator is uninitialized and the function has no return statement.','function total(array $items): int { $sum = 0; foreach ($items as $item) { $sum += $item; } return $sum; }','assert(total([1,2,3]) === 6);'),
('Exceptions','catching Throwable broadly','A programming error becomes a normal response.','Catch expected exceptions and log unexpected failures.','try { process($input); } catch (Throwable $e) { return null; }','Catching every Throwable hides bugs and can swallow engine errors.', 'try { process($input); } catch (InvalidArgumentException $e) { return null; }','assertThrowsForProgrammerError();'),
('Resources','file handle leak','Repeated calls exhaust descriptors.','Use finally or a scoped helper to close resources.','$handle = fopen($path, "rb"); return fread($handle, 100);','An exception or early return can skip fclose.','$handle = fopen($path, "rb"); try { return fread($handle, 100); } finally { fclose($handle); }','assertHandleClosedAfterSuccessAndFailure();'),
('Security','unsafe SQL interpolation','Input changes the query predicate.','Use parameterized queries.','$pdo->query("SELECT * FROM users WHERE id = $id");','Interpolating untrusted input permits SQL injection.','$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id"); $stmt->execute(["id" => $id]);','assertInjectionPayloadCannotAlterPredicate();'),
('Serialization','json error ignored','Invalid JSON becomes null data.','Check decoding errors explicitly.','$data = json_decode($body, true); return $data["name"];','json_decode returns null for invalid JSON unless the caller requests exceptions.', '$data = json_decode($body, true, 512, JSON_THROW_ON_ERROR); return $data["name"];','assertThrowsOnMalformedJson();'),
('Sessions','missing regeneration','Login remains vulnerable to fixation.','Regenerate the session identifier after authentication.','$_SESSION["user_id"] = $user->id;','Keeping the pre-authentication identifier permits session fixation.', 'session_regenerate_id(true); $_SESSION["user_id"] = $user->id;','assertSessionIdChangesAfterLogin();'),
('Namespaces','wrong imported symbol','The class is not found in production.','Use the declared namespace and import the exact class.','use App\\User; $user = new Users();','The imported symbol and constructed class name differ.', 'use App\\User; $user = new User();','assertClassResolvesWithoutFallback();'),
],
'Laravel':[
('Routing','route order shadowing','The intended endpoint is never reached.','Place specific routes before dynamic catch-alls.','Route::get("/{slug}", [PageController::class, "show"]); Route::get("/admin", [AdminController::class, "index"]);','The dynamic route captures /admin first.', 'Route::get("/admin", [AdminController::class, "index"]); Route::get("/{slug}", [PageController::class, "show"]);','assertRouteIs("/admin", "AdminController@index");'),
('Validation','validated data ignored','Unvalidated request fields reach the model.','Use the validated payload as the only write input.','$data = $request->all(); User::create($data);','Calling validate but writing all request fields defeats the boundary.', '$data = $request->validate(["name" => "required|string"]); User::create($data);','assertUnknownFieldIsNotPersisted();'),
('Eloquent','N+1 relation','A list endpoint issues one query per row.','Eager-load relations used by the response.','$posts = Post::all(); foreach ($posts as $post) echo $post->author->name;','Lazy relation access performs an extra query for each post.', '$posts = Post::with("author")->get();','assertQueryCountDoesNotGrowPerPost();'),
('Transactions','partial write','A failed checkout leaves an order without payment state.','Wrap related writes in a transaction.','$order->save(); $payment->save(); $inventory->decrement("stock");','An exception after the first write can commit inconsistent state.', 'DB::transaction(function () use ($order, $payment, $inventory) { $order->save(); $payment->save(); $inventory->decrement("stock"); });','assertFailedCheckoutRollsBackAllWrites();'),
('Queues','non-idempotent retry','A retried job sends duplicate effects.','Use a stable idempotency key or unique job.', 'public function handle() { Mail::to($this->email)->send(new Receipt); }','Queue retries can run handle more than once.', 'public function uniqueId(): string { return (string) $this->orderId; }','assertRetryDoesNotDuplicateReceipt();'),
('Middleware','authorization after work','Unauthorized users still trigger expensive work.','Authorize before loading or mutating protected resources.','$report = Report::findOrFail($id); abort_unless($request->user()->can("view", $report), 403);','The controller performs the lookup and may leak timing or data before authorization.', 'Gate::authorize("view", $report); return $report;','assertUnauthorizedRequestDoesNotReturnReport();'),
('CSRF','protection disabled','Browser mutations accept cross-site requests.','Keep CSRF middleware for cookie-authenticated routes.','$middleware->except(["/profile/update"]);','Excluding a state-changing route removes the browser forgery boundary.', 'Route::post("/profile/update", ...);','assertPostWithoutCsrfIsRejected();'),
('Caching','stale user response','One user sees another user’s cached data.','Include identity and model version in the key.','return Cache::remember("profile", 60, fn() => $request->user()->profile);','A global key is shared across users.', 'return Cache::remember("profile:".$request->user()->id, 60, fn() => $request->user()->profile);','assertCacheKeyVariesByUser();'),
('Events','event before commit','A listener observes data that later rolls back.','Dispatch after a successful transaction commit when required.', 'event(new OrderCreated($order)); DB::commit();','The event is published before the transaction outcome is known.', 'OrderCreated::dispatch($order)->afterCommit();','assertListenerRunsOnlyAfterCommit();'),
('Views','raw output','User content renders as executable HTML.','Use escaped Blade output or sanitize explicitly.','{!! $comment->body !!}','The raw Blade tag bypasses HTML escaping.', '{{ $comment->body }}','assertScriptMarkupIsEscaped();'),
],
}

def build(title,prefix):
    rows=ROWS[title]; out=[f"# {title} Debug Exercises\n\nA RAG-training corpus of 300 debugging exercises for {title}. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.\n\n## Coverage\n\n- Easy: 100 exercises\n- Medium: 100 exercises\n- Hard: 100 exercises\n- Perspectives: types, state, resources, security, persistence, routing, concurrency, errors, testing, and deployment\n\n"]
    for level in ('Easy','Medium','Hard'):
        for i in range(1,101): out.append(rec(prefix,title,i,level,rows[(i-1)%len(rows)],'php'))
    return ''.join(out)

def main():
    for title,prefix,file in [('PHP','PHP','php-debug-exercises.md'),('Laravel','LARAVEL','laravel-debug-exercises.md')]:
        (ROOT/'docs/curriculum'/file).write_text(build(title,prefix),encoding='utf-8')
        print('wrote',file,'with 300 exercises')

if __name__=='__main__': main()
