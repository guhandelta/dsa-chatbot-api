# Ruby on Rails Debug Exercises

A RAG-training corpus of 300 debugging exercises for Ruby on Rails. Each record contains a framework-specific failure, diagnosis, corrected implementation, and regression guidance. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: language semantics, state, memory/ownership, concurrency, errors, APIs, security, persistence, and testing

## RAILS-E-001: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-002: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-003: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-004: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-005: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-006: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-007: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-008: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-009: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-010: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-011: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-012: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-013: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-014: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-015: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-016: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-017: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-018: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-019: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-020: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-021: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-022: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-023: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-024: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-025: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-026: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-027: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-028: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-029: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-030: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-031: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-032: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-033: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-034: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-035: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-036: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-037: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-038: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-039: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-040: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-041: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-042: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-043: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-044: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-045: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-046: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-047: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-048: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-049: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-050: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-051: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-052: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-053: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-054: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-055: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-056: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-057: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-058: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-059: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-060: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-061: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-062: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-063: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-064: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-065: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-066: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-067: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-068: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-069: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-070: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-071: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-072: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-073: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-074: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-075: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-076: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-077: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-078: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-079: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-080: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-081: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-082: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-083: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-084: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-085: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-086: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-087: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-088: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-089: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-090: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-E-091: N+1 association queries

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-E-092: validation bypass

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-E-093: partial state change

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-E-094: strong parameters missing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-E-095: fragment cache key stale

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-E-096: non-idempotent retry

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-E-097: CSRF protection skipped

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-E-098: route order shadowing

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-E-099: unsafe HTML output

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-E-100: missing index

- Difficulty: Easy
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-001: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-002: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-003: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-004: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-005: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-006: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-007: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-008: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-009: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-010: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-011: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-012: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-013: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-014: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-015: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-016: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-017: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-018: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-019: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-020: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-021: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-022: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-023: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-024: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-025: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-026: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-027: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-028: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-029: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-030: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-031: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-032: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-033: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-034: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-035: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-036: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-037: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-038: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-039: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-040: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-041: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-042: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-043: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-044: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-045: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-046: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-047: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-048: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-049: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-050: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-051: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-052: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-053: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-054: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-055: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-056: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-057: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-058: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-059: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-060: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-061: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-062: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-063: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-064: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-065: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-066: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-067: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-068: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-069: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-070: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-071: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-072: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-073: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-074: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-075: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-076: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-077: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-078: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-079: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-080: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-081: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-082: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-083: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-084: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-085: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-086: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-087: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-088: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-089: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-090: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-M-091: N+1 association queries

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-M-092: validation bypass

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-M-093: partial state change

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-M-094: strong parameters missing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-M-095: fragment cache key stale

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-M-096: non-idempotent retry

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-M-097: CSRF protection skipped

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-M-098: route order shadowing

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-M-099: unsafe HTML output

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-M-100: missing index

- Difficulty: Medium
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-001: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-002: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-003: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-004: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-005: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-006: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-007: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-008: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-009: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-010: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-011: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-012: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-013: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-014: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-015: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-016: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-017: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-018: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-019: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-020: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-021: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-022: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-023: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-024: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-025: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-026: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-027: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-028: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-029: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-030: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-031: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-032: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-033: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-034: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-035: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-036: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-037: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-038: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-039: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-040: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-041: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-042: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-043: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-044: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-045: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-046: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-047: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-048: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-049: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-050: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-051: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-052: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-053: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-054: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-055: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-056: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-057: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-058: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-059: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-060: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-061: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-062: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-063: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-064: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-065: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-066: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-067: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-068: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-069: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-070: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-071: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-072: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-073: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-074: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-075: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-076: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-077: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-078: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-079: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-080: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-081: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-082: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-083: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-084: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-085: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-086: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-087: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-088: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-089: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-090: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```

## RAILS-H-091: N+1 association queries

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: N+1 association queries
- Symptom: An index page becomes slow as rows grow.
- Diagnostic goal: Eager-load relations used by the view.

### Buggy code

```ruby
posts = Post.all
posts.each { |post| post.author.name }
```

### Expected diagnosis

Lazy association access issues one query per post.

### Corrected code

```ruby
posts = Post.includes(:author)
```

### Regression tests

```ruby
assert_queries_constant { get :index }
```

## RAILS-H-092: validation bypass

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Active Record
- Concept: validation bypass
- Symptom: Invalid rows enter the database.
- Diagnostic goal: Use model validation and enforce database constraints.

### Buggy code

```ruby
user.update_columns(email: params[:email])
```

### Expected diagnosis

update_columns skips validations and callbacks.

### Corrected code

```ruby
user.update!(email: params[:email])
```

### Regression tests

```ruby
assert_raises(ActiveRecord::RecordInvalid) { invalid_update }
```

## RAILS-H-093: partial state change

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Transactions
- Concept: partial state change
- Symptom: A failed operation leaves half an order saved.
- Diagnostic goal: Wrap related writes in a transaction.

### Buggy code

```ruby
order.save!
charge.save!
shipment.save!
```

### Expected diagnosis

An exception after the first save commits partial state unless a transaction surrounds the work.

### Corrected code

```ruby
ApplicationRecord.transaction { order.save!; charge.save!; shipment.save! }
```

### Regression tests

```ruby
assert_no_partial_records_after_failure
```

## RAILS-H-094: strong parameters missing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Controllers
- Concept: strong parameters missing
- Symptom: Unexpected fields can be assigned.
- Diagnostic goal: Permit only the intended attributes.

### Buggy code

```ruby
User.new(params[:user])
```

### Expected diagnosis

Unfiltered parameters allow mass assignment of protected fields.

### Corrected code

```ruby
User.new(params.require(:user).permit(:name, :email))
```

### Regression tests

```ruby
assert_forbidden_attribute_is_ignored
```

## RAILS-H-095: fragment cache key stale

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Caching
- Concept: fragment cache key stale
- Symptom: Users see an older representation.
- Diagnostic goal: Include record version and relevant identity in the cache key.

### Buggy code

```ruby
cache ["profile"] do
  render user
end
```

### Expected diagnosis

A shared static key ignores which user and which version is rendered.

### Corrected code

```ruby
cache ["profile", user] do
  render user
end
```

### Regression tests

```ruby
assert_cache_varies_by_user_and_version
```

## RAILS-H-096: non-idempotent retry

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Jobs
- Concept: non-idempotent retry
- Symptom: A retry sends a duplicate email or charge.
- Diagnostic goal: Make job effects idempotent and use stable keys.

### Buggy code

```ruby
def perform(order_id)
  Payment.charge(Order.find(order_id))
end
```

### Expected diagnosis

Automatic retries repeat an external side effect without a deduplication key.

### Corrected code

```ruby
def perform(order_id)
  order = Order.find(order_id)
  Payment.charge(order) unless order.charged?
end
```

### Regression tests

```ruby
assert_retry_does_not_duplicate_charge
```

## RAILS-H-097: CSRF protection skipped

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Security
- Concept: CSRF protection skipped
- Symptom: A browser can submit a state-changing request cross-site.
- Diagnostic goal: Keep CSRF protection for cookie-authenticated mutations.

### Buggy code

```ruby
skip_forgery_protection
```

### Expected diagnosis

Disabling verification removes the browser trust boundary.

### Corrected code

```ruby
protect_from_forgery with: :exception
```

### Regression tests

```ruby
assert_post_without_token_is_rejected
```

## RAILS-H-098: route order shadowing

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Routing
- Concept: route order shadowing
- Symptom: The intended route is never reached.
- Diagnostic goal: Order specific routes before catch-all routes.

### Buggy code

```ruby
get "/:slug", to: "pages#show"
get "/admin", to: "admin#index"
```

### Expected diagnosis

The dynamic route consumes /admin before the specific route.

### Corrected code

```ruby
get "/admin", to: "admin#index"
get "/:slug", to: "pages#show"
```

### Regression tests

```ruby
assert_routing("/admin", controller: "admin", action: "index")
```

## RAILS-H-099: unsafe HTML output

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Views
- Concept: unsafe HTML output
- Symptom: User content renders as markup.
- Diagnostic goal: Use escaped output unless content was explicitly sanitized.

### Buggy code

```ruby
<%= raw comment.body %>
```

### Expected diagnosis

raw bypasses Rails escaping for untrusted text.

### Corrected code

```ruby
<%= comment.body %>
```

### Regression tests

```ruby
assert_select_escaped_user_markup
```

## RAILS-H-100: missing index

- Difficulty: Hard
- Language/framework: Ruby / Ruby on Rails
- Perspective: Database
- Concept: missing index
- Symptom: A common lookup degrades with table size.
- Diagnostic goal: Add a database index matching the query predicate.

### Buggy code

```ruby
User.where(email: email).first
```

### Expected diagnosis

Application code cannot compensate for an absent unique/index constraint at scale.

### Corrected code

```ruby
add_index :users, :email, unique: true
```

### Regression tests

```ruby
assert_duplicate_email_rejected_and_query_indexed
```
