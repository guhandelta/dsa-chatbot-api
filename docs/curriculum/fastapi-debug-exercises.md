# Python FastAPI Debug Exercises

A RAG-training corpus of 300 debugging exercises for FastAPI. Each record isolates a framework-specific failure and includes an editorial diagnosis, corrected implementation, and regression guidance. Corrected code is training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: request boundaries, routing, validation, security, persistence, async/concurrency, lifecycle, testing, and deployment

## FAPI-E-001: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-002: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-003: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-004: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-005: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-006: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-007: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-008: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-009: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-010: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-011: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-012: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-013: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-014: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-015: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-016: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-017: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-018: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-019: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-020: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-021: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-022: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-023: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-024: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-025: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-026: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-027: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-028: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-029: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-030: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-031: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-032: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-033: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-034: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-035: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-036: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-037: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-038: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-039: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-040: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-041: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-042: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-043: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-044: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-045: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-046: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-047: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-048: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-049: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-050: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-051: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-052: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-053: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-054: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-055: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-056: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-057: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-058: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-059: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-060: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-061: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-062: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-063: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-064: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-065: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-066: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-067: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-068: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-069: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-070: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-071: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-072: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-073: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-074: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-075: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-076: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-077: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-078: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-079: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-080: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-081: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-082: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-083: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-084: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-085: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-086: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-087: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-088: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-089: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-090: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-E-091: path type omitted

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-E-092: manual unchecked payload

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-E-093: internal fields leaked

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-E-094: blocking call in async route

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-E-095: shared mutable dependency

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-E-096: token accepted without verification

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-E-097: raw exception leaks

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-E-098: critical work scheduled after response

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-E-099: response shape differs from schema

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-E-100: wildcard origin with credentials

- Difficulty: Easy
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-001: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-002: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-003: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-004: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-005: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-006: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-007: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-008: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-009: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-010: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-011: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-012: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-013: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-014: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-015: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-016: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-017: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-018: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-019: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-020: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-021: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-022: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-023: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-024: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-025: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-026: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-027: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-028: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-029: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-030: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-031: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-032: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-033: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-034: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-035: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-036: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-037: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-038: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-039: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-040: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-041: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-042: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-043: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-044: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-045: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-046: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-047: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-048: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-049: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-050: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-051: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-052: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-053: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-054: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-055: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-056: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-057: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-058: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-059: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-060: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-061: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-062: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-063: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-064: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-065: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-066: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-067: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-068: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-069: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-070: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-071: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-072: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-073: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-074: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-075: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-076: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-077: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-078: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-079: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-080: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-081: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-082: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-083: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-084: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-085: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-086: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-087: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-088: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-089: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-090: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-M-091: path type omitted

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-M-092: manual unchecked payload

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-M-093: internal fields leaked

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-M-094: blocking call in async route

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-M-095: shared mutable dependency

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-M-096: token accepted without verification

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-M-097: raw exception leaks

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-M-098: critical work scheduled after response

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-M-099: response shape differs from schema

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-M-100: wildcard origin with credentials

- Difficulty: Medium
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-001: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-002: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-003: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-004: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-005: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-006: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-007: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-008: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-009: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-010: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-011: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-012: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-013: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-014: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-015: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-016: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-017: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-018: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-019: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-020: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-021: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-022: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-023: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-024: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-025: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-026: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-027: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-028: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-029: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-030: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-031: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-032: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-033: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-034: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-035: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-036: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-037: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-038: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-039: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-040: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-041: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-042: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-043: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-044: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-045: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-046: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-047: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-048: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-049: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-050: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-051: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-052: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-053: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-054: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-055: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-056: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-057: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-058: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-059: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-060: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-061: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-062: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-063: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-064: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-065: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-066: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-067: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-068: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-069: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-070: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-071: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-072: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-073: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-074: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-075: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-076: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-077: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-078: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-079: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-080: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-081: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-082: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-083: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-084: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-085: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-086: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-087: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-088: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-089: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-090: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```

## FAPI-H-091: path type omitted

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Validation
- Concept: path type omitted
- Symptom: Invalid identifiers reach database code and produce 500s.
- Diagnostic goal: Declare the path type so FastAPI validates at the boundary.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id):
    return load_user(user_id)
```

### Expected diagnosis

Without an annotation, the framework does not enforce integer input before the handler.

### Corrected code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return load_user(user_id)
```

### Regression tests

```python
# Noninteger path input returns 422; integer input reaches the handler.
```

## FAPI-H-092: manual unchecked payload

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Request model
- Concept: manual unchecked payload
- Symptom: Malformed JSON causes inconsistent errors.
- Diagnostic goal: Use a Pydantic request model for shape and constraints.

### Buggy code

```python
@app.post('/items')
def create(payload: dict):
    return {'name': payload['name']}
```

### Expected diagnosis

A generic dict permits missing fields and produces a KeyError instead of a validation response.

### Corrected code

```python
class ItemIn(BaseModel):
    name: str = Field(min_length=1)

@app.post('/items')
def create(payload: ItemIn):
    return {'name': payload.name}
```

### Regression tests

```python
# Missing and empty names return 422; valid JSON is accepted.
```

## FAPI-H-093: internal fields leaked

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Response model
- Concept: internal fields leaked
- Symptom: The API returns passwords or database metadata.
- Diagnostic goal: Declare an output model that limits serialization.

### Buggy code

```python
@app.get('/users/{user_id}')
def user(user_id: int):
    return db.get_user(user_id)
```

### Expected diagnosis

Returning an ORM or dict directly exposes every serializable field.

### Corrected code

```python
class UserOut(BaseModel):
    id: int
    name: str

@app.get('/users/{user_id}', response_model=UserOut)
def user(user_id: int):
    return db.get_user(user_id)
```

### Regression tests

```python
# Assert response excludes password_hash and private metadata.
```

## FAPI-H-094: blocking call in async route

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Async boundary
- Concept: blocking call in async route
- Symptom: Concurrent requests stall one another.
- Diagnostic goal: Use an async client or a synchronous route for blocking work.

### Buggy code

```python
@app.get('/report')
async def report():
    return requests.get(REPORT_URL).json()
```

### Expected diagnosis

requests.get blocks the event-loop thread inside an async endpoint.

### Corrected code

```python
@app.get('/report')
async def report(client: httpx.AsyncClient):
    response = await client.get(REPORT_URL)
    response.raise_for_status()
    return response.json()
```

### Regression tests

```python
# Concurrent requests remain schedulable while the upstream call is pending.
```

## FAPI-H-095: shared mutable dependency

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Dependency lifetime
- Concept: shared mutable dependency
- Symptom: Requests share a session or user unexpectedly.
- Diagnostic goal: Yield per-request resources and close them after use.

### Buggy code

```python
session = Session()

def get_db():
    return session
```

### Expected diagnosis

A module-level session is shared across requests and may leak state or connections.

### Corrected code

```python
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
```

### Regression tests

```python
# Each request receives a fresh session and teardown closes it.
```

## FAPI-H-096: token accepted without verification

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Authentication
- Concept: token accepted without verification
- Symptom: Any bearer string is treated as an authenticated user.
- Diagnostic goal: Verify signature, expiry, and claims before authorizing.

### Buggy code

```python
def current_user(token: str):
    return decode_unverified(token)
```

### Expected diagnosis

Decoding a token is not verification; an attacker can alter its claims.

### Corrected code

```python
def current_user(token: str):
    claims = jwt.decode(token, SECRET, algorithms=['HS256'])
    if claims.get('exp', 0) < time.time():
        raise HTTPException(status_code=401, detail='expired token')
    return claims
```

### Regression tests

```python
# Forged signatures and expired tokens return 401.
```

## FAPI-H-097: raw exception leaks

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Error contract
- Concept: raw exception leaks
- Symptom: Database details appear in API responses.
- Diagnostic goal: Map expected failures to stable HTTP errors and log unexpected ones.

### Buggy code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    return db.get(item_id)
```

### Expected diagnosis

A missing record or database exception has no explicit HTTP contract.

### Corrected code

```python
@app.get('/items/{item_id}')
def item(item_id: int):
    value = db.get(item_id)
    if value is None:
        raise HTTPException(status_code=404, detail='item not found')
    return value
```

### Regression tests

```python
# Missing item returns 404 with a stable detail; internal failures are handled globally.
```

## FAPI-H-098: critical work scheduled after response

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: Background tasks
- Concept: critical work scheduled after response
- Symptom: The response says success although the task can be lost.
- Diagnostic goal: Use a durable queue for work that must complete.

### Buggy code

```python
@app.post('/emails')
def send(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_invoice)
    return {'queued': True}
```

### Expected diagnosis

In-process background tasks are best-effort and can disappear when the worker exits.

### Corrected code

```python
@app.post('/emails', status_code=202)
def send():
    job = durable_queue.enqueue('send_invoice')
    return {'job_id': job.id}
```

### Regression tests

```python
# The response is 202 and the durable queue owns retry and persistence.
```

## FAPI-H-099: response shape differs from schema

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: OpenAPI contract
- Concept: response shape differs from schema
- Symptom: Generated clients cannot rely on the documented response.
- Diagnostic goal: Keep the response model and returned object aligned.

### Buggy code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return {'identifier': 1}
```

### Expected diagnosis

The returned key does not satisfy the declared response model.

### Corrected code

```python
class ItemOut(BaseModel):
    id: int

@app.get('/item', response_model=ItemOut)
def item():
    return ItemOut(id=1)
```

### Regression tests

```python
# The serialized response contains id and matches the OpenAPI schema.
```

## FAPI-H-100: wildcard origin with credentials

- Difficulty: Hard
- Framework: Python FastAPI
- Perspective: CORS/security
- Concept: wildcard origin with credentials
- Symptom: Any site can make credentialed browser requests.
- Diagnostic goal: Use an explicit origin allowlist when credentials are enabled.

### Buggy code

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True)
```

### Expected diagnosis

Wildcard origins and credentials are incompatible with a safe browser trust boundary.

### Corrected code

```python
app.add_middleware(CORSMiddleware, allow_origins=['https://app.example'], allow_credentials=True)
```

### Regression tests

```python
# Allowed origin receives credentials; an unlisted origin does not.
```
