# Python Django Debug Exercises

A RAG-training corpus of 300 debugging exercises for Django. Each record isolates a framework-specific failure and includes an editorial diagnosis, corrected implementation, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: request boundaries, routing, validation, security, persistence, async/concurrency, lifecycle, testing, and deployment

## DJA-E-001: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-002: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-003: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-004: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-005: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-006: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-007: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-008: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-009: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-010: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-011: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-012: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-013: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-014: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-015: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-016: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-017: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-018: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-019: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-020: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-021: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-022: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-023: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-024: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-025: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-026: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-027: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-028: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-029: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-030: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-031: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-032: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-033: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-034: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-035: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-036: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-037: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-038: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-039: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-040: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-041: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-042: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-043: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-044: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-045: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-046: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-047: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-048: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-049: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-050: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-051: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-052: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-053: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-054: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-055: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-056: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-057: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-058: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-059: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-060: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-061: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-062: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-063: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-064: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-065: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-066: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-067: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-068: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-069: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-070: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-071: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-072: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-073: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-074: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-075: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-076: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-077: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-078: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-079: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-080: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-081: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-082: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-083: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-084: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-085: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-086: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-087: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-088: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-089: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-090: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-E-091: path converter mismatch

- Difficulty: Easy
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-E-092: POST data treated as JSON

- Difficulty: Easy
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-E-093: N+1 related queries

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-E-094: lost update

- Difficulty: Easy
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-E-095: unsafe state-changing form

- Difficulty: Easy
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-E-096: safe filter on user content

- Difficulty: Easy
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-E-097: response returned from middleware incorrectly

- Difficulty: Easy
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-E-098: production settings inherited unsafely

- Difficulty: Easy
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-E-099: authorization checked only in template

- Difficulty: Easy
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-E-100: long task in request

- Difficulty: Easy
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-001: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-002: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-003: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-004: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-005: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-006: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-007: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-008: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-009: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-010: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-011: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-012: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-013: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-014: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-015: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-016: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-017: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-018: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-019: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-020: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-021: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-022: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-023: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-024: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-025: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-026: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-027: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-028: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-029: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-030: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-031: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-032: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-033: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-034: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-035: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-036: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-037: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-038: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-039: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-040: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-041: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-042: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-043: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-044: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-045: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-046: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-047: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-048: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-049: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-050: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-051: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-052: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-053: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-054: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-055: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-056: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-057: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-058: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-059: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-060: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-061: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-062: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-063: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-064: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-065: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-066: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-067: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-068: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-069: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-070: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-071: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-072: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-073: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-074: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-075: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-076: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-077: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-078: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-079: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-080: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-081: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-082: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-083: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-084: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-085: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-086: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-087: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-088: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-089: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-090: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-M-091: path converter mismatch

- Difficulty: Medium
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-M-092: POST data treated as JSON

- Difficulty: Medium
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-M-093: N+1 related queries

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-M-094: lost update

- Difficulty: Medium
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-M-095: unsafe state-changing form

- Difficulty: Medium
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-M-096: safe filter on user content

- Difficulty: Medium
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-M-097: response returned from middleware incorrectly

- Difficulty: Medium
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-M-098: production settings inherited unsafely

- Difficulty: Medium
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-M-099: authorization checked only in template

- Difficulty: Medium
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-M-100: long task in request

- Difficulty: Medium
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-001: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-002: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-003: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-004: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-005: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-006: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-007: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-008: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-009: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-010: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-011: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-012: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-013: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-014: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-015: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-016: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-017: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-018: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-019: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-020: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-021: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-022: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-023: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-024: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-025: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-026: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-027: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-028: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-029: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-030: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-031: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-032: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-033: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-034: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-035: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-036: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-037: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-038: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-039: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-040: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-041: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-042: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-043: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-044: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-045: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-046: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-047: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-048: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-049: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-050: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-051: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-052: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-053: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-054: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-055: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-056: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-057: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-058: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-059: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-060: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-061: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-062: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-063: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-064: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-065: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-066: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-067: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-068: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-069: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-070: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-071: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-072: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-073: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-074: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-075: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-076: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-077: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-078: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-079: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-080: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-081: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-082: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-083: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-084: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-085: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-086: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-087: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-088: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-089: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-090: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```

## DJA-H-091: path converter mismatch

- Difficulty: Hard
- Framework: Python Django
- Perspective: URL routing
- Concept: path converter mismatch
- Symptom: A route never reaches the view for a valid-looking value.
- Diagnostic goal: Match the URL pattern to the view parameter and domain type.

### Buggy code

```python
path('orders/<int:order_id>/', views.order)
```

### Expected diagnosis

The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.

### Corrected code

```python
path('orders/<uuid:order_id>/', views.order)
```

### Regression tests

```python
# UUID URLs reach the view; malformed UUIDs return 404.
```

## DJA-H-092: POST data treated as JSON

- Difficulty: Hard
- Framework: Python Django
- Perspective: Request parsing
- Concept: POST data treated as JSON
- Symptom: JSON clients see missing fields or a 400 response.
- Diagnostic goal: Parse JSON explicitly and validate the decoded object.

### Buggy code

```python
def create(request):
    name = request.POST['name']
    return JsonResponse({'name': name})
```

### Expected diagnosis

request.POST parses form encoding, not an application/json body.

### Corrected code

```python
def create(request):
    try:
        data = json.loads(request.body)
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        return JsonResponse({'error': 'name required'}, status=400)
    return JsonResponse({'name': data['name']})
```

### Regression tests

```python
# JSON and form clients follow explicit, tested contracts.
```

## DJA-H-093: N+1 related queries

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM query behavior
- Concept: N+1 related queries
- Symptom: A list page becomes slow as rows grow.
- Diagnostic goal: Load related objects in the query plan instead of the template loop.

### Buggy code

```python
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

### Expected diagnosis

Each customer access can issue another query when the relation is not eagerly loaded.

### Corrected code

```python
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)
```

### Regression tests

```python
# Assert query count stays constant as the number of orders grows.
```

## DJA-H-094: lost update

- Difficulty: Hard
- Framework: Python Django
- Perspective: ORM update
- Concept: lost update
- Symptom: Two requests overwrite one another's changes.
- Diagnostic goal: Make read-modify-write atomic at the database boundary.

### Buggy code

```python
account.balance -= amount
account.save()
```

### Expected diagnosis

Separate reads and writes permit concurrent requests to use the same old balance.

### Corrected code

```python
with transaction.atomic():
    account = Account.objects.select_for_update().get(pk=account_id)
    if account.balance < amount:
        raise ValueError('insufficient funds')
    account.balance -= amount
    account.save(update_fields=['balance'])
```

### Regression tests

```python
# Concurrent withdrawals never produce a negative balance or lost update.
```

## DJA-H-095: unsafe state-changing form

- Difficulty: Hard
- Framework: Python Django
- Perspective: CSRF boundary
- Concept: unsafe state-changing form
- Symptom: A browser can submit a state-changing request from another site.
- Diagnostic goal: Apply CSRF protection to cookie-authenticated mutations.

### Buggy code

```python
def delete(request, pk):
    if request.method == 'POST':
        Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Expected diagnosis

A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.

### Corrected code

```python
@require_POST
@csrf_protect
def delete(request, pk):
    Item.objects.filter(pk=pk).delete()
    return redirect('items')
```

### Regression tests

```python
# Missing or invalid CSRF token is rejected; a valid token permits deletion.
```

## DJA-H-096: safe filter on user content

- Difficulty: Hard
- Framework: Python Django
- Perspective: Template escaping
- Concept: safe filter on user content
- Symptom: Stored text renders as executable markup.
- Diagnostic goal: Leave untrusted template values escaped.

### Buggy code

```python
{{ comment.body|safe }}
```

### Expected diagnosis

The safe filter bypasses Django's default HTML escaping.

### Corrected code

```python
{{ comment.body }}
```

### Regression tests

```python
# A comment containing '<img onerror=...>' is rendered as text.
```

## DJA-H-097: response returned from middleware incorrectly

- Difficulty: Hard
- Framework: Python Django
- Perspective: Middleware
- Concept: response returned from middleware incorrectly
- Symptom: Requests fail before reaching the view.
- Diagnostic goal: Preserve the middleware callable contract.

### Buggy code

```python
def middleware(get_response):
    def handler(request):
        get_response(request)
        return HttpResponse('ok')
    return handler
```

### Expected diagnosis

The downstream response is discarded, so every request receives the middleware's replacement response.

### Corrected code

```python
def middleware(get_response):
    def handler(request):
        response = get_response(request)
        response['X-Request-Checked'] = '1'
        return response
    return handler
```

### Regression tests

```python
# The original status and body survive while the header is added.
```

## DJA-H-098: production settings inherited unsafely

- Difficulty: Hard
- Framework: Python Django
- Perspective: Settings
- Concept: production settings inherited unsafely
- Symptom: Debug or permissive hosts remain enabled in deployment.
- Diagnostic goal: Make environment-specific security settings explicit.

### Buggy code

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Expected diagnosis

Debug output and wildcard hosts are unsafe production defaults.

### Corrected code

```python
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
```

### Regression tests

```python
# Production environment yields DEBUG=False and an explicit host list.
```

## DJA-H-099: authorization checked only in template

- Difficulty: Hard
- Framework: Python Django
- Perspective: Authentication
- Concept: authorization checked only in template
- Symptom: A hidden button does not prevent direct access.
- Diagnostic goal: Enforce authorization in the view or permission layer.

### Buggy code

```python
{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}
```

### Expected diagnosis

Template visibility is presentation logic; it does not protect the endpoint.

### Corrected code

```python
@user_passes_test(lambda user: user.is_staff)
def delete(request):
    ...
```

### Regression tests

```python
# A nonstaff direct request receives 403/redirect; staff can proceed.
```

## DJA-H-100: long task in request

- Difficulty: Hard
- Framework: Python Django
- Perspective: Background work
- Concept: long task in request
- Symptom: Requests time out and workers are exhausted.
- Diagnostic goal: Move durable work to a task system and return a trackable result.

### Buggy code

```python
def export(request):
    build_large_export()
    return JsonResponse({'status': 'done'})
```

### Expected diagnosis

Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.

### Corrected code

```python
def export(request):
    job = export_task.delay(request.user.id)
    return JsonResponse({'job_id': job.id}, status=202)
```

### Regression tests

```python
# The endpoint returns quickly with 202 and a job identifier.
```
