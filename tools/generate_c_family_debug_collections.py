"""Generate separate C, C++, C#, and .NET debugging corpora."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rec(prefix, language, i, level, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests, fence):
    if fence == 'python':
        ast.parse(fixed)
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/platform: {language}
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


def c_rows(n):
    return [
        ("Memory safety", "off-by-one allocation", "The last byte is overwritten.", "Match allocation size to the largest valid index.", f"char *copy{n}(const char *s) {{\n    size_t n = strlen(s);\n    char *out = malloc(n);\n    memcpy(out, s, n + 1);\n    return out;\n}}", "The terminator requires n + 1 bytes; copying n + 1 bytes into n bytes is a heap overflow.", f"char *copy{n}(const char *s) {{\n    size_t n = strlen(s);\n    char *out = malloc(n + 1);\n    if (!out) return NULL;\n    memcpy(out, s, n + 1);\n    return out;\n}}", f"// Assert copy{n}(\"abc\") is \"abc\" and allocation failure is handled."),
        ("Pointer lifetime", "returning address of local", "The caller reads garbage.", "Ensure returned storage outlives the function.", f"int *value{n}(void) {{ int result = 7; return &result; }}", "A pointer to an automatic local object becomes invalid when the function returns.", f"int value{n}(void) {{ return 7; }}", f"assert(value{n}() == 7);"),
        ("String API", "missing terminator", "Printing reads beyond the buffer.", "Reserve and write the C string terminator.", f"char name{n}[4];\nmemcpy(name{n}, \"Ada\", 3);\nprintf(\"%s\", name{n});", "memcpy copies bytes only and does not append a terminator.", f"char name{n}[4];\nmemcpy(name{n}, \"Ada\", 3);\nname{n}[3] = '\\0';", f"assert(strcmp(name{n}, \"Ada\") == 0);"),
        ("Integer reasoning", "signed overflow", "A boundary calculation produces undefined behavior.", "Check before arithmetic or use an unsigned/wider representation.", f"int total{n}(int count, int size) {{ return count * size; }}", "Signed overflow is undefined in C; validating after the multiplication is too late.", f"bool total{n}(int count, int size, int *out) {{\n    if (count < 0 || size < 0 || count > INT_MAX / size) return false;\n    *out = count * size;\n    return true;\n}}", f"// Assert overflow returns false and a safe product returns true."),
        ("Ownership", "double free", "The allocator reports corruption.", "Assign ownership once and clear moved-from pointers.", f"void release{n}(char **p) {{ free(*p); free(*p); }}", "Freeing the same allocation twice is undefined behavior.", f"void release{n}(char **p) {{\n    if (p && *p) {{ free(*p); *p = NULL; }}\n}}", f"// Call release{n} twice; the second call is harmless."),
        ("I/O contract", "unchecked fopen", "A null FILE pointer is dereferenced.", "Check resource acquisition before use.", f"FILE *f = fopen(path, \"r\");\nchar line[64];\nfgets(line, sizeof line, f);", "fopen returns NULL on failure; passing it to fgets is undefined behavior.", f"FILE *f = fopen(path, \"r\");\nif (!f) return ERROR_OPEN;\nchar line[64];\nif (!fgets(line, sizeof line, f)) {{ fclose(f); return ERROR_READ; }}\nfclose(f);", f"// Missing paths return an error without dereferencing NULL."),
        ("Concurrency", "data race", "A counter loses increments under threads.", "Synchronize shared mutable state.", f"shared_count{n}++;", "Concurrent unsynchronized read-modify-write accesses form a data race and have undefined behavior.", f"pthread_mutex_lock(&count_mutex);\nshared_count{n}++;\npthread_mutex_unlock(&count_mutex);", f"// Run two workers and assert the final count equals both contributions."),
        ("Parsing", "scanf width omission", "Long input corrupts adjacent memory.", "Bound formatted input by the destination capacity.", f"char word{n}[16];\nscanf(\"%s\", word{n});", "The conversion has no width limit, so input longer than 15 characters overflows the array.", f"char word{n}[16];\nscanf(\"%15s\", word{n});", f"// A 100-character token must not overwrite memory."),
        ("API contract", "strncpy non-termination", "The result is not a valid string for exact-length input.", "Terminate explicitly after bounded copying.", f"strncpy(dst{n}, src{n}, sizeof dst{n});\nprintf(\"%s\", dst{n});", "strncpy does not append a terminator when the source fills the limit.", f"strncpy(dst{n}, src{n}, sizeof dst{n} - 1);\ndst{n}[sizeof dst{n} - 1] = '\\0';", f"// Exact-capacity source remains safely printable."),
        ("Cleanup", "early return leak", "An error path leaks an allocation.", "Centralize cleanup for all exits.", f"char *buffer = malloc(1024);\nif (!buffer) return 0;\nif (!read_data(buffer)) return -1;\nfree(buffer);\nreturn 0;", "The failed read returns before freeing buffer.", f"char *buffer = malloc(1024);\nif (!buffer) return 0;\nint result = read_data(buffer) ? 0 : -1;\nfree(buffer);\nreturn result;", f"// Both read success and failure leave no allocation outstanding."),
    ]


def cpp_rows(n):
    return [
        ("RAII", "manual cleanup", "An exception leaks a resource.", "Bind ownership to an object lifetime.", f"FILE *file{n} = fopen(path, \"r\");\nif (!file{n}) throw std::runtime_error(\"open\");\nprocess(file{n});\nfclose(file{n});", "An exception from process skips fclose.", f"struct FileCloser{n} {{ void operator()(FILE *p) const {{ if (p) fclose(p); }} }};\nusing File{n} = std::unique_ptr<FILE, FileCloser{n}>;\nFile{n} file{n}(fopen(path, \"r\"));\nif (!file{n}) throw std::runtime_error(\"open\");\nprocess(file{n}.get());", f"// Throw from process and verify the file is still closed."),
        ("Move semantics", "use after move", "The source object is assumed to retain its value.", "Treat moved-from objects as valid but unspecified.", f"std::string first{n} = \"data\";\nstd::string second{n} = std::move(first{n});\nuse(first{n});", "Moving transfers resources; using the source as if it still contains the old value is a contract error.", f"std::string first{n} = \"data\";\nstd::string second{n} = std::move(first{n});\nuse(second{n});", f"// Assert second{n} contains data; do not depend on first{n}'s value."),
        ("Iterator validity", "erase invalidates iterator", "The loop skips elements or crashes.", "Use the iterator returned by erase.", f"for (auto it = values.begin(); it != values.end(); ++it) {{\n    if (*it < 0) values.erase(it);\n}}", "erase invalidates it; incrementing it afterward is undefined behavior.", f"for (auto it = values.begin(); it != values.end();) {{\n    if (*it < 0) it = values.erase(it);\n    else ++it;\n}}", f"// [-1,-2,3] becomes [3] without invalid iterator use."),
        ("Templates", "dangling reference", "A returned reference points to a temporary.", "Return by value or reference only to an object with sufficient lifetime.", f"const std::string& label{n}() {{ return std::string(\"ok\"); }}", "The temporary is destroyed at the end of the return expression.", f"std::string label{n}() {{ return std::string(\"ok\"); }}", f"assert(label{n}() == \"ok\");"),
        ("Exception safety", "partial mutation", "An operation leaves an object half updated.", "Prepare changes before committing them.", f"void rename{n}(User &u, std::string name) {{ u.name = std::move(name); validate(u); }}", "If validation throws, the object has already been mutated.", f"void rename{n}(User &u, std::string name) {{\n    User candidate = u;\n    candidate.name = std::move(name);\n    validate(candidate);\n    u = std::move(candidate);\n}}", f"// Invalid names leave u unchanged."),
        ("Ownership", "shared ownership cycle", "Objects are never destroyed.", "Use weak_ptr for non-owning back references.", f"struct Node{n} {{ std::shared_ptr<Node{n}> parent; std::shared_ptr<Node{n}> child; }};", "A parent-child cycle keeps both reference counts nonzero.", f"struct Node{n} {{ std::weak_ptr<Node{n}> parent; std::shared_ptr<Node{n}> child; }};", f"// Destroying the root releases the child graph."),
        ("Concurrency", "mutex not exception safe", "A thrown operation deadlocks later callers.", "Use scoped locking.", f"mutex.lock();\nupdate();\nmutex.unlock();", "An exception skips unlock.", f"std::lock_guard<std::mutex> guard(mutex);\nupdate();", f"// Throwing from update still permits a later lock."),
        ("Numeric correctness", "unsigned underflow", "A reverse loop never terminates.", "Use a signed index or an iterator for reverse traversal.", f"for (size_t i = values.size() - 1; i >= 0; --i) use(values[i]);", "size_t cannot become negative, so the condition remains true after zero.", f"for (auto it = values.rbegin(); it != values.rend(); ++it) use(*it);", f"// Empty and one-element vectors both terminate."),
        ("Polymorphism", "missing virtual destructor", "Deleting through a base pointer leaks derived resources.", "Make a polymorphic base destructor virtual.", f"struct Base{n} {{ ~Base{n}() {{}} virtual void run() = 0; }};", "Deleting a derived object through Base without a virtual destructor is undefined behavior.", f"struct Base{n} {{ virtual ~Base{n}() = default; virtual void run() = 0; }};", f"// unique_ptr<Base{n}> destroys a derived instance completely."),
        ("API contract", "copying expensive object", "A hot path allocates unexpectedly.", "Pass large read-only values by const reference.", f"void inspect{n}(std::vector<int> values) {{ use(values); }}", "Passing by value copies the vector and may allocate.", f"void inspect{n}(const std::vector<int>& values) {{ use(values); }}", f"// Instrumented vector confirms no copy occurs."),
    ]


def cs_rows(n):
    return [
        ("Nullability", "null dereference", "A request fails with NullReferenceException.", "Validate nullable values before dereferencing.", f"string name{n} = user.Profile.Name;", "The compiler/runtime contract does not guarantee Profile or Name exists.", f"string name{n} = user.Profile?.Name ?? \"unknown\";", f"// Null profile yields 'unknown'; populated profile yields its name."),
        ("Async", "missing await", "The caller receives a task instead of a result.", "Await the asynchronous operation and propagate cancellation.", f"public string Load{n}() => client.GetStringAsync(url).Result;", "Blocking on Result can deadlock a synchronization context and hides asynchronous failure.", f"public async Task<string> Load{n}(CancellationToken token) => await client.GetStringAsync(url, token);", f"// Cancellation is propagated and no synchronous wait occurs."),
        ("LINQ", "deferred query after disposal", "Enumeration fails after the data source is closed.", "Materialize inside the resource lifetime when needed.", f"IEnumerable<string> Names{n}() {{ using var db = Open(); return db.Users.Select(u => u.Name); }}", "LINQ is deferred; the returned query enumerates after db is disposed.", f"IReadOnlyList<string> Names{n}() {{ using var db = Open(); return db.Users.Select(u => u.Name).ToList(); }}", f"// The returned list remains usable after the context closes."),
        ("Collections", "mutating during foreach", "InvalidOperationException is thrown.", "Build a removal list or iterate a snapshot.", f"foreach (var item in items) if (item.IsExpired) items.Remove(item);", "List enumeration detects structural modification.", f"items.RemoveAll(item => item.IsExpired);", f"// All expired items are removed and active items remain."),
        ("Disposal", "owned dependency disposed twice", "A shared stream fails when another component uses it.", "Make ownership explicit and dispose only the owner.", f"using var stream = sharedStream;\nRead(stream);", "Disposing a borrowed resource invalidates the component that owns it.", f"Read(sharedStream);", f"// The owner remains responsible for disposing sharedStream."),
        ("Serialization", "public field omitted", "JSON lacks a required property.", "Configure the serializer contract or use properties.", f"public class Item{n} {{ public int id; }}", "The default serializer contract commonly includes public properties, not fields.", f"public class Item{n} {{ public int Id {{ get; set; }} }}", f"// Serialized JSON contains the expected Id property."),
        ("Exceptions", "catching all exceptions", "Programming defects become success responses.", "Catch only expected failures and preserve diagnostics.", f"try {{ Save(); }} catch (Exception) {{ return true; }}", "Catching Exception hides cancellation, bugs, and environmental failures.", f"try {{ Save(); return true; }} catch (ValidationException) {{ return false; }}", f"// Validation failure is reported; unexpected exceptions propagate."),
        ("Concurrency", "shared mutable singleton", "Requests observe one another's state.", "Use scoped state or synchronization for mutable data.", f"services.AddSingleton<Cart{n}>();", "A singleton carrying per-user mutable state is shared across all requests.", f"services.AddScoped<Cart{n}>();", f"// Two scopes receive independent carts."),
        ("Configuration", "missing required setting", "The app starts and fails later with a null value.", "Validate configuration at startup.", f"var url{n} = config[\"ServiceUrl\"];\nclient.BaseAddress = new Uri(url{n});", "A missing setting becomes a delayed null/format failure.", f"var url{n} = config[\"ServiceUrl\"] ?? throw new InvalidOperationException(\"ServiceUrl required\");\nclient.BaseAddress = new Uri(url{n});", f"// Startup fails clearly when ServiceUrl is absent."),
        ("Equality", "reference equality", "Equivalent value objects do not compare equal.", "Implement value equality or use a value type/record.", f"class Point{n} {{ public int X; public int Y; }}\nif (a == b) {{ ... }}", "Classes default to reference equality unless equality is overridden.", f"record Point{n}(int X, int Y);\nif (a == b) {{ ... }}", f"// Two Point{n}(1,2) values compare equal."),
    ]


def dotnet_rows(n):
    return [
        ("Dependency injection", "wrong service lifetime", "A scoped dependency is resolved from a singleton.", "Align lifetimes with ownership and request scope.", f"services.AddSingleton<ReportService{n}>();\nservices.AddScoped<DbContext{n}>();", "A singleton cannot safely capture a scoped service; the container reports a lifetime violation or leaks request state.", f"services.AddScoped<ReportService{n}>();\nservices.AddScoped<DbContext{n}>();", f"// Provider validation passes and each request gets a scoped report service."),
        ("ASP.NET routing", "ambiguous route", "Requests match the wrong action or fail startup.", "Make route templates and constraints unambiguous.", f"[HttpGet(\"{{id}}\")]\npublic IActionResult Get(string id) => Ok(id);\n[HttpGet(\"{{id}}\")]\npublic IActionResult GetByNumber(int id) => Ok(id);", "Two actions have the same route shape and differ only by CLR parameter type, which may not disambiguate routing.", f"[HttpGet(\"{{id}}\")]\npublic IActionResult Get(string id) => Ok(id);\n[HttpGet(\"{{id:int}}\")]\npublic IActionResult GetByNumber(int id) => Ok(id);", f"// Text and integer routes select the intended action."),
        ("Middleware", "short-circuit omission", "A response is written twice or the pipeline continues after a terminal response.", "Return immediately when middleware owns the response.", f"if (!authorized) {{ context.Response.StatusCode = 401; }}\nawait next(context);", "Unauthorized requests still reach downstream middleware and may overwrite the response.", f"if (!authorized) {{ context.Response.StatusCode = 401; return; }}\nawait next(context);", f"// Unauthorized requests never invoke the downstream delegate."),
        ("Configuration", "environment secret in source", "Production uses a development credential.", "Load secrets from managed configuration providers.", f"builder.Configuration[\"ApiKey\"] = \"dev-key\";", "Source-controlled secrets are exposed and override deployment configuration.", f"var key = builder.Configuration[\"ApiKey\"] ?? throw new InvalidOperationException(\"ApiKey required\");", f"// Startup fails without configured ApiKey and never embeds a secret."),
        ("Serialization", "reference loop", "JSON serialization throws or emits an enormous graph.", "Shape DTOs to the API boundary instead of serializing the entity graph.", f"return Results.Json(order{n});", "Bidirectional navigation properties can create cycles and expose persistence details.", f"return Results.Ok(new OrderDto{n}(order{n}.Id, order{n}.Total));", f"// Response contains only the documented DTO fields."),
        ("EF Core", "query executed after context disposal", "Enumeration throws ObjectDisposedException.", "Materialize within the context or keep the context alive through enumeration.", f"IQueryable<Item{n}> Query{n}() {{ using var db = new AppDbContext(); return db.Items.Where(x => x.Active); }}", "IQueryable is deferred; the database access happens after the context is disposed.", f"IReadOnlyList<Item{n}> Query{n}() {{ using var db = new AppDbContext(); return db.Items.Where(x => x.Active).ToList(); }}", f"// The returned list can be enumerated after Query{n} returns."),
        ("Hosted services", "unhandled background exception", "A worker stops silently or takes down the host.", "Observe failures and define restart behavior.", f"protected override async Task ExecuteAsync(CancellationToken token) {{ while (!token.IsCancellationRequested) await WorkAsync(); }}", "An exception escapes the loop without logging or a deliberate recovery policy.", f"protected override async Task ExecuteAsync(CancellationToken token) {{ while (!token.IsCancellationRequested) {{ try {{ await WorkAsync(token); }} catch (Exception ex) when (!token.IsCancellationRequested) {{ logger.LogError(ex, \"worker failed\"); await Task.Delay(TimeSpan.FromSeconds(1), token); }} }} }}", f"// Transient failure is logged and retried; cancellation exits cleanly."),
        ("HTTP clients", "new client per request", "Sockets exhaust under load.", "Use IHttpClientFactory or a long-lived handler-managed client.", f"using var client = new HttpClient();\nreturn await client.GetAsync(url);", "Creating and disposing clients per request can exhaust ephemeral ports and prevent connection reuse.", f"return await httpClient.GetAsync(url, token);", f"// The injected client is reused and supports cancellation."),
        ("Authorization", "authentication confused with authorization", "Any signed-in user can access an admin operation.", "Require the policy or role for the operation.", f"[Authorize]\npublic IActionResult Delete(int id) => Ok();", "[Authorize] proves identity but does not require the administrator policy.", f"[Authorize(Policy = \"AdminOnly\")]\npublic IActionResult Delete(int id) => Ok();", f"// Authenticated nonadmins receive 403; admins may delete."),
        ("Health checks", "health endpoint checks no dependency", "Orchestrator keeps a broken instance in service.", "Separate liveness from readiness and check critical dependencies.", f"app.MapHealthChecks(\"/health\");", "A process-level endpoint can be healthy while its database or queue is unavailable.", f"app.MapHealthChecks(\"/ready\", new HealthCheckOptions {{ Predicate = check => check.Tags.Contains(\"ready\") }});", f"// Readiness fails when a tagged critical dependency is unavailable."),
    ]


def build(framework, prefix, fence, rows):
    text = f"""# {framework} Debug Exercises

A RAG-training corpus of 300 debugging exercises for {framework}. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: memory and ownership, concurrency, API contracts, persistence, validation, security, lifecycle, testing, and deployment

"""
    for level in ('Easy', 'Medium', 'Hard'):
        for i in range(1, 101):
            text += rec(prefix, framework, i, level, *rows[(i - 1) % len(rows)], fence)
    return text


def main():
    specs = [
        ('C', 'C', 'c', c_rows, 'c-debug-exercises.md'),
        ('C++', 'CPP', 'cpp', cpp_rows, 'cpp-debug-exercises.md'),
        ('C#', 'CS', 'csharp', cs_rows, 'csharp-debug-exercises.md'),
        ('.NET', 'NET', 'csharp', dotnet_rows, 'dotnet-debug-exercises.md'),
    ]
    for framework, prefix, fence, fn, filename in specs:
        path = ROOT / 'docs/curriculum' / filename
        path.write_text(build(framework, prefix, fence, fn(1)), encoding='utf-8')
        print(f'wrote {path} with 300 exercises')


if __name__ == '__main__':
    main()
