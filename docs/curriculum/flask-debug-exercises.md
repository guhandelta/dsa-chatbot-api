# Python Flask Debug Exercises

A RAG-training corpus of 300 debugging exercises for Flask. Each record isolates a framework-specific failure and includes an editorial diagnosis, corrected implementation, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: request boundaries, routing, validation, security, persistence, async/concurrency, lifecycle, testing, and deployment

## FLK-E-001: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-002: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-003: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-004: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-005: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-006: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-007: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-008: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-009: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-010: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-011: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-012: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-013: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-014: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-015: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-016: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-017: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-018: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-019: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-020: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-021: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-022: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-023: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-024: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-025: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-026: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-027: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-028: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-029: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-030: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-031: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-032: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-033: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-034: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-035: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-036: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-037: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-038: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-039: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-040: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-041: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-042: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-043: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-044: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-045: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-046: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-047: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-048: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-049: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-050: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-051: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-052: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-053: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-054: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-055: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-056: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-057: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-058: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-059: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-060: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-061: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-062: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-063: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-064: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-065: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-066: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-067: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-068: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-069: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-070: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-071: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-072: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-073: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-074: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-075: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-076: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-077: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-078: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-079: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-080: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-081: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-082: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-083: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-084: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-085: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-086: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-087: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-088: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-089: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-090: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-E-091: route parameter mismatch

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-E-092: JSON body assumption

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-E-093: implicit string response

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-E-094: global request state

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-E-095: broad exception handler

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-E-096: unescaped output

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-E-097: missing secret configuration

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-E-098: connection never closed

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-E-099: cache key omits identity

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-E-100: debug mode in production

- Difficulty: Easy
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-001: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-002: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-003: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-004: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-005: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-006: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-007: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-008: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-009: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-010: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-011: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-012: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-013: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-014: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-015: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-016: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-017: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-018: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-019: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-020: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-021: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-022: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-023: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-024: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-025: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-026: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-027: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-028: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-029: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-030: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-031: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-032: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-033: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-034: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-035: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-036: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-037: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-038: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-039: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-040: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-041: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-042: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-043: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-044: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-045: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-046: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-047: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-048: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-049: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-050: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-051: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-052: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-053: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-054: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-055: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-056: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-057: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-058: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-059: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-060: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-061: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-062: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-063: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-064: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-065: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-066: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-067: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-068: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-069: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-070: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-071: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-072: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-073: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-074: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-075: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-076: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-077: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-078: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-079: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-080: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-081: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-082: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-083: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-084: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-085: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-086: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-087: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-088: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-089: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-090: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-M-091: route parameter mismatch

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-M-092: JSON body assumption

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-M-093: implicit string response

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-M-094: global request state

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-M-095: broad exception handler

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-M-096: unescaped output

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-M-097: missing secret configuration

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-M-098: connection never closed

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-M-099: cache key omits identity

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-M-100: debug mode in production

- Difficulty: Medium
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-001: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-002: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-003: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-004: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-005: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-006: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-007: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-008: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-009: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-010: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-011: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-012: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-013: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-014: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-015: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-016: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-017: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-018: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-019: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-020: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-021: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-022: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-023: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-024: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-025: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-026: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-027: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-028: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-029: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-030: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-031: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-032: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-033: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-034: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-035: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-036: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-037: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-038: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-039: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-040: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-041: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-042: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-043: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-044: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-045: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-046: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-047: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-048: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-049: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-050: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-051: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-052: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-053: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-054: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-055: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-056: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-057: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-058: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-059: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-060: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-061: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-062: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-063: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-064: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-065: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-066: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-067: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-068: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-069: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-070: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-071: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-072: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-073: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-074: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-075: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-076: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-077: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-078: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-079: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-080: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-081: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-082: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-083: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-084: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-085: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-086: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-087: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-088: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-089: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-090: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```

## FLK-H-091: route parameter mismatch

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Routing
- Concept: route parameter mismatch
- Symptom: A valid URL returns 404 or raises a conversion error.
- Diagnostic goal: Align the route converter with the view contract.

### Buggy code

```python
@app.get('/users/<int:user_id>')
def user(user_id):
    return str(user_id)
```

### Expected diagnosis

The route declares an integer converter, so nonnumeric path segments cannot reach the view.

### Corrected code

```python
@app.get('/users/<int:user_id>')
def user(user_id: int):
    return {'id': user_id}
```

### Regression tests

```python
# GET /users/7 returns 200; GET /users/nope returns 404.
```

## FLK-H-092: JSON body assumption

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Request boundary
- Concept: JSON body assumption
- Symptom: A malformed or absent body causes a server error.
- Diagnostic goal: Validate optional JSON before reading fields.

### Buggy code

```python
@app.post('/items')
def create():
    data = request.get_json()
    return {'name': data['name']}
```

### Expected diagnosis

get_json can return None or raise for malformed input; indexing it turns client errors into 500 responses.

### Corrected code

```python
@app.post('/items')
def create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('name'), str):
        abort(400, description='name is required')
    return {'name': data['name']}
```

### Regression tests

```python
# Assert malformed JSON and missing name return 400; valid JSON returns 200.
```

## FLK-H-093: implicit string response

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Response contract
- Concept: implicit string response
- Symptom: Clients receive inconsistent content types.
- Diagnostic goal: Return an explicit JSON response for an API endpoint.

### Buggy code

```python
@app.get('/health')
def health():
    return 'ok'
```

### Expected diagnosis

A bare string is a text response, not a stable JSON object contract.

### Corrected code

```python
@app.get('/health')
def health():
    return jsonify(status='ok')
```

### Regression tests

```python
# Assert content type is application/json and body is {'status': 'ok'}.
```

## FLK-H-094: global request state

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Application state
- Concept: global request state
- Symptom: Concurrent requests overwrite one another's data.
- Diagnostic goal: Keep request-specific values in request-local context.

### Buggy code

```python
current_user = None

@app.before_request
def load_user():
    global current_user
    current_user = lookup(request.headers.get('Authorization'))
```

### Expected diagnosis

A module global is shared by requests and is unsafe under threaded or async servers.

### Corrected code

```python
@app.before_request
def load_user():
    g.current_user = lookup(request.headers.get('Authorization'))
```

### Regression tests

```python
# Two request contexts must retain independent g.current_user values.
```

## FLK-H-095: broad exception handler

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Error handling
- Concept: broad exception handler
- Symptom: Programming defects become misleading 400 responses.
- Diagnostic goal: Handle expected client failures narrowly.

### Buggy code

```python
@app.errorhandler(Exception)
def error(exc):
    return {'error': str(exc)}, 400
```

### Expected diagnosis

Catching every exception hides server defects and leaks internal messages to clients.

### Corrected code

```python
@app.errorhandler(ValueError)
def value_error(exc):
    return {'error': str(exc)}, 400

@app.errorhandler(Exception)
def server_error(exc):
    app.logger.exception('unhandled request error')
    return {'error': 'internal server error'}, 500
```

### Regression tests

```python
# ValueError maps to 400; an unexpected exception maps to 500 without details.
```

## FLK-H-096: unescaped output

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Template safety
- Concept: unescaped output
- Symptom: User text can inject markup into a page.
- Diagnostic goal: Use the template engine's escaping boundary.

### Buggy code

```python
return render_template_string('<p>{{ text|safe }}</p>', text=request.args.get('text', ''))
```

### Expected diagnosis

The safe filter disables escaping for untrusted request data.

### Corrected code

```python
return render_template_string('<p>{{ text }}</p>', text=request.args.get('text', ''))
```

### Regression tests

```python
# A '<script>' query value must appear escaped in the response.
```

## FLK-H-097: missing secret configuration

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Session security
- Concept: missing secret configuration
- Symptom: Sessions are forgeable or the app fails in production.
- Diagnostic goal: Require a strong secret from deployment configuration.

### Buggy code

```python
app.secret_key = 'development-secret'
```

### Expected diagnosis

A checked-in predictable key allows session tampering and is unsafe across environments.

### Corrected code

```python
app.secret_key = os.environ['FLASK_SECRET_KEY']
```

### Regression tests

```python
# Startup without FLASK_SECRET_KEY fails clearly; configured startup uses the secret.
```

## FLK-H-098: connection never closed

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Database lifecycle
- Concept: connection never closed
- Symptom: Connections accumulate across requests.
- Diagnostic goal: Use application-context teardown to release request resources.

### Buggy code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db
```

### Expected diagnosis

The cached connection has no teardown path, so workers leak connections.

### Corrected code

```python
def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Regression tests

```python
# Teardown closes an opened connection and is safe when none was opened.
```

## FLK-H-099: cache key omits identity

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Caching
- Concept: cache key omits identity
- Symptom: One user's response is served to another user.
- Diagnostic goal: Include all authorization-relevant inputs in cache policy.

### Buggy code

```python
@cache.cached(timeout=60)
def profile():
    return jsonify(load_profile())
```

### Expected diagnosis

A shared route cache can reuse a personalized response without varying by user.

### Corrected code

```python
@cache.cached(timeout=60, unless=lambda: not getattr(g, 'current_user', None))
def profile():
    return jsonify(load_profile(g.current_user.id))
```

### Regression tests

```python
# Assert anonymous requests are not cached and authenticated keys vary by user.
```

## FLK-H-100: debug mode in production

- Difficulty: Hard
- Framework: Python Flask
- Perspective: Deployment
- Concept: debug mode in production
- Symptom: The debugger exposes internals or restarts unpredictably.
- Diagnostic goal: Separate local debugging from production configuration.

### Buggy code

```python
app.run(debug=True)
```

### Expected diagnosis

Werkzeug's debugger is for development and can expose execution capabilities.

### Corrected code

```python
app.run(debug=os.environ.get('FLASK_ENV') == 'development')
```

### Regression tests

```python
# Production configuration must evaluate debug=False.
```
