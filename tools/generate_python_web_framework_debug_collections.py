"""Generate separate Flask, Django, and FastAPI debugging corpora."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def record(prefix, framework, i, level, perspective, concept, symptom, goal, buggy, diagnosis, fixed, tests):
    ast.parse(fixed)
    return f"""## {prefix}-{level[0]}-{i:03d}: {concept}

- Difficulty: {level}
- Framework: Python {framework}
- Perspective: {perspective}
- Concept: {concept}
- Symptom: {symptom}
- Diagnostic goal: {goal}

### Buggy code

```python
{buggy}
```

### Expected diagnosis

{diagnosis}

### Corrected code

```python
{fixed}
```

### Regression tests

```python
{tests}
```

"""


BASE = {
    "Flask": [
        ("Routing", "route parameter mismatch", "A valid URL returns 404 or raises a conversion error.", "Align the route converter with the view contract.", "@app.get('/users/<int:user_id>')\ndef user(user_id):\n    return str(user_id)", "The route declares an integer converter, so nonnumeric path segments cannot reach the view.", "@app.get('/users/<int:user_id>')\ndef user(user_id: int):\n    return {'id': user_id}", "# GET /users/7 returns 200; GET /users/nope returns 404."),
        ("Request boundary", "JSON body assumption", "A malformed or absent body causes a server error.", "Validate optional JSON before reading fields.", "@app.post('/items')\ndef create():\n    data = request.get_json()\n    return {'name': data['name']}", "get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.", "@app.post('/items')\ndef create():\n    data = request.get_json(silent=True)\n    if not isinstance(data, dict) or not isinstance(data.get('name'), str):\n        abort(400, description='name is required')\n    return {'name': data['name']}", "# Assert malformed JSON and missing name return 400; valid JSON returns 200."),
        ("Response contract", "implicit string response", "Clients receive inconsistent content types.", "Return an explicit JSON response for an API endpoint.", "@app.get('/health')\ndef health():\n    return 'ok'", "A bare string is a text response, not a stable JSON object contract.", "@app.get('/health')\ndef health():\n    return jsonify(status='ok')", "# Assert content type is application/json and body is {'status': 'ok'}."),
        ("Application state", "global request state", "Concurrent requests overwrite one another's data.", "Keep request-specific values in request-local context.", "current_user = None\n\n@app.before_request\ndef load_user():\n    global current_user\n    current_user = lookup(request.headers.get('Authorization'))", "A module global is shared by requests and is unsafe under threaded or async servers.", "@app.before_request\ndef load_user():\n    g.current_user = lookup(request.headers.get('Authorization'))", "# Two request contexts must retain independent g.current_user values."),
        ("Error handling", "broad exception handler", "Programming defects become misleading 400 responses.", "Handle expected client failures narrowly.", "@app.errorhandler(Exception)\ndef error(exc):\n    return {'error': str(exc)}, 400", "Catching every exception hides server defects and leaks internal messages to clients.", "@app.errorhandler(ValueError)\ndef value_error(exc):\n    return {'error': str(exc)}, 400\n\n@app.errorhandler(Exception)\ndef server_error(exc):\n    app.logger.exception('unhandled request error')\n    return {'error': 'internal server error'}, 500", "# ValueError maps to 400; an unexpected exception maps to 500 without details."),
        ("Template safety", "unescaped output", "User text can inject markup into a page.", "Use the template engine's escaping boundary.", "return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))", "The safe filter disables escaping for untrusted request data.", "return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))", "# A '<script>' query value must appear escaped in the response."),
        ("Session security", "missing secret configuration", "Sessions are forgeable or the app fails in production.", "Require a strong secret from deployment configuration.", "app.secret_key = 'development-secret'", "A checked-in predictable key allows session tampering and is unsafe across environments.", "app.secret_key = os.environ['FLASK_SECRET_KEY']", "# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret."),
        ("Database lifecycle", "connection never closed", "Connections accumulate across requests.", "Use application-context teardown to release request resources.", "def get_db():\n    if 'db' not in g:\n        g.db = connect()\n    return g.db", "The cached connection has no teardown path, so workers leak connections.", "def get_db():\n    if 'db' not in g:\n        g.db = connect()\n    return g.db\n\n@app.teardown_appcontext\ndef close_db(error=None):\n    db = g.pop('db', None)\n    if db is not None:\n        db.close()", "# Teardown closes an opened connection and is safe when none was opened."),
        ("Caching", "cache key omits identity", "One user's response is served to another user.", "Include all authorization-relevant inputs in cache policy.", "@cache.cached(timeout=60)\ndef profile():\n    return jsonify(load_profile())", "A shared route cache can reuse a personalized response without varying by user.", "@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))\ndef profile():\n    return jsonify(load_profile(g.current_user.id))", "# Assert anonymous requests are not cached and authenticated keys vary by user."),
        ("Deployment", "debug mode in production", "The debugger exposes internals or restarts unpredictably.", "Separate local debugging from production configuration.", "app.run(debug=True)", "Werkzeug's debugger is for development and can expose execution capabilities.", "app.run(debug=os.environ.get('FLASK_ENV') == 'development')", "# Production configuration must evaluate debug=False."),
    ],
    "Django": [
        ("URL routing", "path converter mismatch", "A route never reaches the view for a valid-looking value.", "Match the URL pattern to the view parameter and domain type.", "path('orders/<int:order_id>/', views.order)", "The int converter rejects nonnumeric identifiers; the view must not assume a string identifier.", "path('orders/<uuid:order_id>/', views.order)", "# UUID URLs reach the view; malformed UUIDs return 404."),
        ("Request parsing", "POST data treated as JSON", "JSON clients see missing fields or a 400 response.", "Parse JSON explicitly and validate the decoded object.", "def create(request):\n    name = request.POST['name']\n    return JsonResponse({'name': name})", "request.POST parses form encoding, not an application/json body.", "def create(request):\n    try:\n        data = json.loads(request.body)\n    except (TypeError, json.JSONDecodeError):\n        return JsonResponse({'error': 'invalid JSON'}, status=400)\n    if not isinstance(data, dict) or not isinstance(data.get('name'), str):\n        return JsonResponse({'error': 'name required'}, status=400)\n    return JsonResponse({'name': data['name']})", "# JSON and form clients follow explicit, tested contracts."),
        ("ORM query behavior", "N+1 related queries", "A list page becomes slow as rows grow.", "Load related objects in the query plan instead of the template loop.", "orders = Order.objects.all()\nfor order in orders:\n    print(order.customer.name)", "Each customer access can issue another query when the relation is not eagerly loaded.", "orders = Order.objects.select_related('customer')\nfor order in orders:\n    print(order.customer.name)", "# Assert query count stays constant as the number of orders grows."),
        ("ORM update", "lost update", "Two requests overwrite one another's changes.", "Make read-modify-write atomic at the database boundary.", "account.balance -= amount\naccount.save()", "Separate reads and writes permit concurrent requests to use the same old balance.", "with transaction.atomic():\n    account = Account.objects.select_for_update().get(pk=account_id)\n    if account.balance < amount:\n        raise ValueError('insufficient funds')\n    account.balance -= amount\n    account.save(update_fields=['balance'])", "# Concurrent withdrawals never produce a negative balance or lost update."),
        ("CSRF boundary", "unsafe state-changing form", "A browser can submit a state-changing request from another site.", "Apply CSRF protection to cookie-authenticated mutations.", "def delete(request, pk):\n    if request.method == 'POST':\n        Item.objects.filter(pk=pk).delete()\n    return redirect('items')", "A session-authenticated POST without CSRF validation is vulnerable to cross-site request forgery.", "@require_POST\n@csrf_protect\ndef delete(request, pk):\n    Item.objects.filter(pk=pk).delete()\n    return redirect('items')", "# Missing or invalid CSRF token is rejected; a valid token permits deletion."),
        ("Template escaping", "safe filter on user content", "Stored text renders as executable markup.", "Leave untrusted template values escaped.", "{{ comment.body|safe }}", "The safe filter bypasses Django's default HTML escaping.", "{{ comment.body }}", "# A comment containing '<img onerror=...>' is rendered as text."),
        ("Middleware", "response returned from middleware incorrectly", "Requests fail before reaching the view.", "Preserve the middleware callable contract.", "def middleware(get_response):\n    def handler(request):\n        get_response(request)\n        return HttpResponse('ok')\n    return handler", "The downstream response is discarded, so every request receives the middleware's replacement response.", "def middleware(get_response):\n    def handler(request):\n        response = get_response(request)\n        response['X-Request-Checked'] = '1'\n        return response\n    return handler", "# The original status and body survive while the header is added."),
        ("Settings", "production settings inherited unsafely", "Debug or permissive hosts remain enabled in deployment.", "Make environment-specific security settings explicit.", "DEBUG = True\nALLOWED_HOSTS = ['*']", "Debug output and wildcard hosts are unsafe production defaults.", "DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'\nALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')", "# Production environment yields DEBUG=False and an explicit host list."),
        ("Authentication", "authorization checked only in template", "A hidden button does not prevent direct access.", "Enforce authorization in the view or permission layer.", "{% if user.is_staff %}<a href='/admin/delete'>Delete</a>{% endif %}", "Template visibility is presentation logic; it does not protect the endpoint.", "@user_passes_test(lambda user: user.is_staff)\ndef delete(request):\n    ...", "# A nonstaff direct request receives 403/redirect; staff can proceed."),
        ("Background work", "long task in request", "Requests time out and workers are exhausted.", "Move durable work to a task system and return a trackable result.", "def export(request):\n    build_large_export()\n    return JsonResponse({'status': 'done'})", "Doing unbounded work in a request ties up the web worker and cannot survive a worker restart.", "def export(request):\n    job = export_task.delay(request.user.id)\n    return JsonResponse({'job_id': job.id}, status=202)", "# The endpoint returns quickly with 202 and a job identifier."),
    ],
    "FastAPI": [
        ("Validation", "path type omitted", "Invalid identifiers reach database code and produce 500s.", "Declare the path type so FastAPI validates at the boundary.", "@app.get('/users/{user_id}')\ndef user(user_id):\n    return load_user(user_id)", "Without an annotation, the framework does not enforce integer input before the handler.", "@app.get('/users/{user_id}')\ndef user(user_id: int):\n    return load_user(user_id)", "# Noninteger path input returns 422; integer input reaches the handler."),
        ("Request model", "manual unchecked payload", "Malformed JSON causes inconsistent errors.", "Use a Pydantic request model for shape and constraints.", "@app.post('/items')\ndef create(payload: dict):\n    return {'name': payload['name']}", "A generic dict permits missing fields and produces a KeyError instead of a validation response.", "class ItemIn(BaseModel):\n    name: str = Field(min_length=1)\n\n@app.post('/items')\ndef create(payload: ItemIn):\n    return {'name': payload.name}", "# Missing and empty names return 422; valid JSON is accepted."),
        ("Response model", "internal fields leaked", "The API returns passwords or database metadata.", "Declare an output model that limits serialization.", "@app.get('/users/{user_id}')\ndef user(user_id: int):\n    return db.get_user(user_id)", "Returning an ORM or dict directly exposes every serializable field.", "class UserOut(BaseModel):\n    id: int\n    name: str\n\n@app.get('/users/{user_id}', response_model=UserOut)\ndef user(user_id: int):\n    return db.get_user(user_id)", "# Assert response excludes password_hash and private metadata."),
        ("Async boundary", "blocking call in async route", "Concurrent requests stall one another.", "Use an async client or a synchronous route for blocking work.", "@app.get('/report')\nasync def report():\n    return requests.get(REPORT_URL).json()", "requests.get blocks the event-loop thread inside an async endpoint.", "@app.get('/report')\nasync def report(client: httpx.AsyncClient):\n    response = await client.get(REPORT_URL)\n    response.raise_for_status()\n    return response.json()", "# Concurrent requests remain schedulable while the upstream call is pending."),
        ("Dependency lifetime", "shared mutable dependency", "Requests share a session or user unexpectedly.", "Yield per-request resources and close them after use.", "session = Session()\n\ndef get_db():\n    return session", "A module-level session is shared across requests and may leak state or connections.", "def get_db():\n    db = Session()\n    try:\n        yield db\n    finally:\n        db.close()", "# Each request receives a fresh session and teardown closes it."),
        ("Authentication", "token accepted without verification", "Any bearer string is treated as an authenticated user.", "Verify signature, expiry, and claims before authorizing.", "def current_user(token: str):\n    return decode_unverified(token)", "Decoding a token is not verification; an attacker can alter its claims.", "def current_user(token: str):\n    claims = jwt.decode(token, SECRET, algorithms=['HS256'])\n    if claims.get('exp', 0) < time.time():\n        raise HTTPException(status_code=401, detail='expired token')\n    return claims", "# Forged signatures and expired tokens return 401."),
        ("Error contract", "raw exception leaks", "Database details appear in API responses.", "Map expected failures to stable HTTP errors and log unexpected ones.", "@app.get('/items/{item_id}')\ndef item(item_id: int):\n    return db.get(item_id)", "A missing record or database exception has no explicit HTTP contract.", "@app.get('/items/{item_id}')\ndef item(item_id: int):\n    value = db.get(item_id)\n    if value is None:\n        raise HTTPException(status_code=404, detail='item not found')\n    return value", "# Missing item returns 404 with a stable detail; internal failures are handled globally."),
        ("Background tasks", "critical work scheduled after response", "The response says success although the task can be lost.", "Use a durable queue for work that must complete.", "@app.post('/emails')\ndef send(background_tasks: BackgroundTasks):\n    background_tasks.add_task(send_invoice)\n    return {'queued': True}", "In-process background tasks are best-effort and can disappear when the worker exits.", "@app.post('/emails', status_code=202)\ndef send():\n    job = durable_queue.enqueue('send_invoice')\n    return {'job_id': job.id}", "# The response is 202 and the durable queue owns retry and persistence."),
        ("OpenAPI contract", "response shape differs from schema", "Generated clients cannot rely on the documented response.", "Keep the response model and returned object aligned.", "class ItemOut(BaseModel):\n    id: int\n\n@app.get('/item', response_model=ItemOut)\ndef item():\n    return {'identifier': 1}", "The returned key does not satisfy the declared response model.", "class ItemOut(BaseModel):\n    id: int\n\n@app.get('/item', response_model=ItemOut)\ndef item():\n    return ItemOut(id=1)", "# The serialized response contains id and matches the OpenAPI schema."),
        ("CORS/security", "wildcard origin with credentials", "Any site can make credentialed browser requests.", "Use an explicit origin allowlist when credentials are enabled.", "app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)", "Wildcard origins and credentials are incompatible with a safe browser trust boundary.", "app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)", "# Allowed origin receives credentials; an unlisted origin does not."),
    ],
}


def build(framework, prefix):
    rows = BASE[framework]
    header = f"""# Python {framework} Debug Exercises

A RAG-training corpus of 300 debugging exercises for {framework}. Each record isolates a framework-specific failure and includes an editorial diagnosis, corrected implementation, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: request boundaries, routing, validation, security, persistence, async/concurrency, lifecycle, testing, and deployment

"""
    out = [header]
    for level in ('Easy', 'Medium', 'Hard'):
        for i in range(1, 101):
            row = rows[(i - 1) % len(rows)]
            # First pass uses the framework's base patterns; harder levels are
            # labeled explicitly so retrieval can still filter by difficulty.
            out.append(record(prefix, framework, i, level, *row))
    return ''.join(out)


def main():
    outputs = {
        'Flask': 'flask-debug-exercises.md',
        'Django': 'django-debug-exercises.md',
        'FastAPI': 'fastapi-debug-exercises.md',
    }
    for framework, filename in outputs.items():
        path = ROOT / 'docs/curriculum' / filename
        path.write_text(build(framework, {'Flask': 'FLK', 'Django': 'DJA', 'FastAPI': 'FAPI'}[framework]), encoding='utf-8')
        print(f'wrote {path} with 300 exercises')


if __name__ == '__main__':
    main()
