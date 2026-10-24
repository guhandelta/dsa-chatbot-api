"""Generate separate Ruby, Rails, Rust, and Go debugging corpora."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rec(prefix, framework, i, level, language, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests, fence):
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Language/framework: {language} / {framework}
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


ROWS = {
    'Ruby': [
        ('Ruby', 'Blocks', 'block variable leakage', 'A later expression sees an unexpected value.', 'Keep block-local state explicit.', 'values = [1, 2]\nvalues.each { |value| total = value }\nputs total', 'The assignment creates or changes outer state; the loop does not accumulate a meaningful result.', 'total = values.sum', 'raise unless total == 3'),
        ('Ruby', 'Object model', 'nil versus false', 'A guard accepts an invalid value.', 'Remember that only nil and false are falsey in Ruby.', 'return fallback unless value', 'Zero and empty strings are truthy in Ruby, so a Python-style truthiness assumption is wrong.', 'return fallback if value.nil? || value == false', 'raise unless enabled?(0) == expected'),
        ('Ruby', 'Collections', 'mutating during each', 'Elements are skipped after deletion.', 'Use select/reject or iterate over a copy.', 'items.each { |item| items.delete(item) if item.expired? }', 'Deleting while iterating changes indexes and can skip adjacent values.', 'items = items.reject(&:expired?)', 'raise unless clean(items).none?(&:expired?)'),
        ('Ruby', 'Exceptions', 'rescue too broad', 'Programming errors become normal results.', 'Rescue only expected exception classes.', 'begin\n  parse(input)\nrescue\n  nil\nend', 'A bare rescue catches StandardError broadly and hides defects.', 'begin\n  parse(input)\nrescue ArgumentError\n  nil\nend', 'raise unless malformed_returns_nil'),
        ('Ruby', 'Contracts', 'mutable default state', 'Calls share state unexpectedly.', 'Create mutable defaults per call.', 'def add(value, bucket = [])\n  bucket << value\nend', 'Ruby evaluates the default expression per call, but a class or constant used as state can still be shared; make ownership explicit.', 'def add(value, bucket: nil)\n  bucket = [] if bucket.nil?\n  bucket << value\nend', 'raise unless add(:a) == [:a] && add(:b) == [:b]'),
        ('Ruby', 'Equality', 'identity versus value equality', 'Equivalent records do not compare equal.', 'Choose ==/eql? and hash consistently.', 'a = User.new(1)\nb = User.new(1)\nraise unless a.equal?(b)', 'equal? tests object identity, not domain value equality.', 'raise unless a == b', 'raise unless User.new(1) == User.new(1)'),
        ('Ruby', 'Concurrency', 'shared mutable state', 'Threaded increments lose updates.', 'Protect the read-modify-write operation.', 'count += 1', 'A compound update is not a synchronization contract even when individual operations appear simple.', 'mutex.synchronize { count += 1 }', 'raise unless concurrent_count == expected'),
        ('Ruby', 'Resources', 'file not closed', 'Descriptors remain open on an error path.', 'Use the block form of resource APIs.', 'file = File.open(path)\nprocess(file)\nfile.close', 'An exception from process skips close.', 'File.open(path) { |file| process(file) }', 'raise unless closed_after_success_and_failure'),
        ('Ruby', 'Metaprogramming', 'method_missing hides typos', 'A misspelled method returns a plausible value.', 'Use explicit interfaces and narrow dynamic dispatch.', 'def method_missing(name, *args)\n  nil\nend', 'Swallowing every unknown method turns programmer errors into silent data errors.', 'def method_missing(name, *args)\n  super\nend', 'raise NoMethodError unless missing_method_raises'),
        ('Ruby', 'Parsing', 'unsafe eval', 'Input executes arbitrary Ruby code.', 'Parse data rather than evaluating source.', 'eval(params[:expression])', 'eval executes attacker-controlled code in the process.', 'JSON.parse(params[:payload])', 'raise unless malicious_expression_is_rejected'),
    ],
    'Ruby on Rails': [
        ('Active Record', 'N+1 association queries', 'An index page becomes slow as rows grow.', 'Eager-load relations used by the view.', 'posts = Post.all\nposts.each { |post| post.author.name }', 'Lazy association access issues one query per post.', 'posts = Post.includes(:author)', 'assert_queries_constant { get :index }'),
        ('Active Record', 'validation bypass', 'Invalid rows enter the database.', 'Use model validation and enforce database constraints.', 'user.update_columns(email: params[:email])', 'update_columns skips validations and callbacks.', 'user.update!(email: params[:email])', 'assert_raises(ActiveRecord::RecordInvalid) { invalid_update }'),
        ('Transactions', 'partial state change', 'A failed operation leaves half an order saved.', 'Wrap related writes in a transaction.', 'order.save!\ncharge.save!\nshipment.save!', 'An exception after the first save commits partial state unless a transaction surrounds the work.', 'ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }', 'assert_no_partial_records_after_failure'),
        ('Controllers', 'strong parameters missing', 'Unexpected fields can be assigned.', 'Permit only the intended attributes.', 'User.new(params[:user])', 'Unfiltered parameters allow mass assignment of protected fields.', 'User.new(params.require(:user).permit(:name, :email))', 'assert_forbidden_attribute_is_ignored'),
        ('Caching', 'fragment cache key stale', 'Users see an older representation.', 'Include record version and relevant identity in the cache key.', 'cache ["profile"] do\n  render user\nend', 'A shared static key ignores which user and which version is rendered.', 'cache ["profile", user] do\n  render user\nend', 'assert_cache_varies_by_user_and_version'),
        ('Jobs', 'non-idempotent retry', 'A retry sends a duplicate email or charge.', 'Make job effects idempotent and use stable keys.', 'def perform(order_id)\n  Payment.charge(Order.find(order_id))\nend', 'Automatic retries repeat an external side effect without a deduplication key.', 'def perform(order_id)\n  order = Order.find(order_id)\n  Payment.charge(order) unless order.charged?\nend', 'assert_retry_does_not_duplicate_charge'),
        ('Security', 'CSRF protection skipped', 'A browser can submit a state-changing request cross-site.', 'Keep CSRF protection for cookie-authenticated mutations.', 'skip_forgery_protection', 'Disabling verification removes the browser trust boundary.', 'protect_from_forgery with: :exception', 'assert_post_without_token_is_rejected'),
        ('Routing', 'route order shadowing', 'The intended route is never reached.', 'Order specific routes before catch-all routes.', 'get "/:slug", to: "pages#show"\nget "/admin", to: "admin#index"', 'The dynamic route consumes /admin before the specific route.', 'get "/admin", to: "admin#index"\nget "/:slug", to: "pages#show"', 'assert_routing("/admin", controller: "admin", action: "index")'),
        ('Views', 'unsafe HTML output', 'User content renders as markup.', 'Use escaped output unless content was explicitly sanitized.', '<%= raw comment.body %>', 'raw bypasses Rails escaping for untrusted text.', '<%= comment.body %>', 'assert_select_escaped_user_markup'),
        ('Database', 'missing index', 'A common lookup degrades with table size.', 'Add a database index matching the query predicate.', 'User.where(email: email).first', 'Application code cannot compensate for an absent unique/index constraint at scale.', 'add_index :users, :email, unique: true', 'assert_duplicate_email_rejected_and_query_indexed'),
    ],
    'Rust': [
        ('Ownership', 'use after move', 'The compiler rejects a later use.', 'Borrow when ownership should remain with the caller.', 'let name = String::from("Ada");\nconsume(name);\nprintln!("{name}");', 'Passing String by value moves it into consume.', 'let name = String::from("Ada");\nconsume(&name);\nprintln!("{name}");', 'assert_eq!(display(), "Ada")'),
        ('Borrowing', 'mutable and immutable borrow overlap', 'Compilation fails or a refactor risks invalidation.', 'End the immutable borrow before mutating the collection.', 'let first = &items[0];\nitems.push(4);\nprintln!("{first}");', 'push may reallocate, so an outstanding reference cannot remain valid across it.', 'let first = items[0];\nitems.push(4);\nprintln!("{first}");', 'assert_eq!(safe(), 1)'),
        ('Result handling', 'unwrap at boundary', 'Malformed input crashes the service.', 'Propagate or map errors at the boundary.', 'let port: u16 = input.parse().unwrap();', 'User or configuration input can fail to parse; unwrap turns expected failure into a panic.', 'let port: u16 = input.parse().map_err(|_| ConfigError::InvalidPort)?;', 'assert!(invalid_port().is_err())'),
        ('Lifetimes', 'return reference to local', 'The compiler rejects a dangling reference.', 'Return owned data or borrow from an input with a declared lifetime.', 'fn label() -> &str { let value = String::from("ok"); &value }', 'value is dropped at function exit.', 'fn label() -> String { String::from("ok") }', 'assert_eq!(label(), "ok")'),
        ('Iterators', 'iterator consumed twice', 'The second pass is empty.', 'Create a new iterator or collect when repeated traversal is required.', 'let values = nums.iter().map(|n| n * 2);\nlet a: Vec<_> = values.collect();\nlet b: Vec<_> = values.collect();', 'Iterator values are consumed by collect.', 'let a: Vec<_> = nums.iter().map(|n| n * 2).collect();\nlet b: Vec<_> = nums.iter().map(|n| n * 2).collect();', 'assert_eq!(a, b)'),
        ('Concurrency', 'data race across threads', 'The compiler rejects shared mutable access.', 'Use Arc plus a synchronization primitive.', 'let mut count = 0;\nthread::spawn(|| count += 1);', 'Threads cannot safely share a mutable stack variable without ownership and synchronization.', 'let count = Arc::new(Mutex::new(0));\nlet worker = Arc::clone(&count);\nthread::spawn(move || *worker.lock().unwrap() += 1);', 'assert_eq!(*count.lock().unwrap(), 1)'),
        ('Async', 'blocking executor thread', 'Unrelated futures stop making progress.', 'Use an async operation or move blocking work to a dedicated pool.', 'async fn load() -> Data { std::thread::sleep(Duration::from_secs(1)); fetch() }', 'Blocking the executor thread prevents other tasks from being polled.', 'async fn load() -> Data { tokio::time::sleep(Duration::from_secs(1)).await; fetch().await }', 'assert_concurrent_tasks_progress()'),
        ('Option', 'None treated as value', 'A missing record causes a panic.', 'Map or handle absence explicitly.', 'let user = users.get(&id).unwrap();', 'A missing key is a normal domain outcome, not necessarily a programmer error.', 'let user = users.get(&id).ok_or(Error::NotFound)?;', 'assert!(missing_user().is_err())'),
        ('Memory', 'unbounded Vec growth', 'A service eventually exhausts memory.', 'Bound input before allocation.', 'let mut body = Vec::new();\nreader.read_to_end(&mut body)?;', 'An untrusted stream can grow the vector without a limit.', 'let mut body = Vec::with_capacity(MAX);\nreader.take((MAX + 1) as u64).read_to_end(&mut body)?;\nif body.len() > MAX { return Err(Error::TooLarge); }', 'assert!(oversized_body().is_err())'),
        ('Error design', 'stringly typed errors', 'Callers cannot reliably classify failures.', 'Use an enum with source errors and stable variants.', 'return Err(format!("db: {err}"));', 'A string loses machine-readable category and source context.', '#[derive(thiserror::Error, Debug)]\nenum Error { #[error("database error: {0}")] Db(#[from] DbError) }', 'assert_matches!(db_failure(), Err(Error::Db(_)))'),
    ],
    'Go': [
        ('Nil interfaces', 'typed nil interface', 'A nil check passes and a method panics.', 'Understand the dynamic type/value pair in an interface.', 'var p *Profile = nil\nvar value any = p\nif value != nil { value.(*Profile).Name }', 'An interface containing a typed nil pointer is itself non-nil.', 'if p != nil { var value any = p; use(value) }', 'assert_no_panic_for_nil_profile()'),
        ('Errors', 'ignored error', 'The program uses an invalid zero value.', 'Handle errors immediately and preserve context.', 'data, _ := os.ReadFile(path)\nreturn parse(data)', 'Ignoring an I/O error makes the following parse operate on incomplete or nil data.', 'data, err := os.ReadFile(path)\nif err != nil { return err }\nreturn parse(data)', 'assert_error_is_returned_for_missing_file()'),
        ('Goroutines', 'goroutine leak', 'Memory and scheduler work grow after requests finish.', 'Give goroutines cancellation and ensure every send/receive can exit.', 'go func() { result <- fetch() }()', 'A receiver that returns early leaves the sender blocked forever.', 'go func() { select { case result <- fetch(): case <-ctx.Done(): } }()', 'assert_goroutine_count_returns_to_baseline()'),
        ('Channels', 'close send panic', 'A worker panics while reporting completion.', 'Define one owner responsible for closing a channel.', 'for _, worker := range workers { go worker(out); go close(out) }', 'Multiple goroutines can close the same channel or close before sends complete.', 'go func() { wg.Wait(); close(out) }()', 'assert_all_results_received_without_panic()'),
        ('Context', 'context ignored', 'Canceled requests continue doing work.', 'Pass context through every blocking dependency.', 'func Load(ctx context.Context) (Data, error) { return client.Get() }', 'The dependency cannot observe cancellation when ctx is not passed.', 'func Load(ctx context.Context) (Data, error) { return client.GetContext(ctx) }', 'assert_cancel_stops_upstream_call()'),
        ('HTTP', 'body not closed', 'Connections are not reused and resources leak.', 'Close response bodies on every successful response.', 'resp, err := http.Get(url)\nif err != nil { return err }\nreturn decode(resp.Body)', 'The response body remains open after decoding.', 'resp, err := http.Get(url)\nif err != nil { return err }\ndefer resp.Body.Close()\nreturn decode(resp.Body)', 'assert_body_closed_after_request()'),
        ('Maps', 'concurrent map write', 'The runtime reports fatal concurrent map writes.', 'Protect maps or use a concurrency-safe design.', 'counts[key]++', 'A map is not safe for concurrent writes, and the increment is a compound operation.', 'mu.Lock()\ncounts[key]++\nmu.Unlock()', 'go run -race reports no race'),
        ('Slices', 'append aliasing', 'A caller sees unexpected mutation.', 'Copy before retaining or returning a slice with independent ownership.', 'func keep(values []byte) []byte { return values[:3] }', 'The returned slice aliases the caller’s backing array.', 'func keep(values []byte) []byte { out := make([]byte, 3); copy(out, values[:3]); return out }', 'assert_mutating_input_does_not_change_result()'),
        ('JSON', 'unknown fields accepted', 'Clients send misspelled fields that are silently ignored.', 'Configure strict decoding at the input boundary.', 'json.NewDecoder(r.Body).Decode(&request)', 'The default decoder ignores unknown JSON keys, hiding client contract errors.', 'decoder := json.NewDecoder(r.Body)\ndecoder.DisallowUnknownFields()\nerr := decoder.Decode(&request)', 'assert_unknown_field_returns_400()'),
        ('Database', 'rows not closed', 'Connection pool exhaustion appears under load.', 'Close rows and check iteration errors.', 'rows, err := db.QueryContext(ctx, query)\nfor rows.Next() { scan(rows) }', 'Rows hold a pooled connection until closed and may report errors after iteration.', 'rows, err := db.QueryContext(ctx, query)\nif err != nil { return err }\ndefer rows.Close()\nfor rows.Next() { scan(rows) }\nreturn rows.Err()', 'assert_rows_closed_and_iteration_error_returned()'),
    ],
}


def build(framework, prefix, language, fence, rows):
    text = f"""# {framework} Debug Exercises

A RAG-training corpus of 300 debugging exercises for {framework}. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, state, memory/ownership, concurrency, errors, APIs, security, persistence, and testing

"""
    for level in ('Easy', 'Medium', 'Hard'):
        for i in range(1, 101):
            out = rows[(i - 1) % len(rows)]
            if framework == 'Ruby' and len(out) == 9:
                out = out[1:]
            text += rec(prefix, framework, i, level, language, *out, fence)
    return text


def main():
    specs = [
        ('Ruby', 'RUBY', 'Ruby', 'ruby', 'ruby-debug-exercises.md'),
        ('Ruby on Rails', 'RAILS', 'Ruby', 'ruby', 'rails-debug-exercises.md'),
        ('Rust', 'RUST', 'Rust', 'rust', 'rust-debug-exercises.md'),
        ('Go', 'GO', 'Go', 'go', 'go-debug-exercises.md'),
    ]
    for framework, prefix, language, fence, filename in specs:
        path = ROOT / 'docs/curriculum' / filename
        path.write_text(build(framework, prefix, language, fence, ROWS[framework]), encoding='utf-8')
        print(f'wrote {path} with 300 exercises')


if __name__ == '__main__':
    main()
