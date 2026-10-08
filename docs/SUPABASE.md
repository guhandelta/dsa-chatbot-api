# Moving to Supabase

Supabase gives you Postgres (relational data), pgvector (embeddings), and auth
in one place. This covers both halves.

They are **independent** — you can move vectors without touching auth and vice
versa. Doing them separately is the lower-risk path.

---

## Part 1 — Vectors (pgvector)

### 1. Enable the extension

In the Supabase SQL editor:

```sql
create extension if not exists vector;
```

### 2. Point the app at Postgres

```bash
VECTOR_STORE=pgvector

# Supabase → Project Settings → Database → Connection string → URI.
# Use the POOLER (6543) for the app; the direct connection (5432) for migrations.
# Percent-encode special characters in the password.
DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

Vectors reuse `DATABASE_URL` by default. Set `VECTOR_DATABASE_URL` only if
embeddings live in a different database.

### 3. Install the driver and re-ingest

```bash
pip install -r requirements.txt
alembic upgrade head
python -m app.services.knowledge_base
```

Re-ingesting is **mandatory**: embeddings live inside the vector store, so
switching backends starts from an empty index. Same one-off cost as the first
ingest.

### What does NOT change

Every call site — `similarity_search`, `add_documents`, `delete`, and the
metadata filters on `track` and `problem_id` — is identical across backends.
Incremental upsert from the training pipeline, track-scoped retrieval, and the
analyzer's exact-id lookup all work unchanged. That is why this is a config
change rather than a rewrite.

### Pooler caveat

Supabase's transaction-mode pooler (6543) does not support prepared
statements. If you see `prepared statement "__asyncpg_1__" already exists`,
either use session mode (5432) or disable statement caching:

```python
create_async_engine(url, connect_args={"statement_cache_size": 0})
```

### Cost note

Embeddings are billed by OpenAI wherever vectors are stored — moving to
pgvector changes storage and query cost, not embedding cost. At 25 documents
storage is negligible either way. The reason to move is operational (one
database, horizontal scaling), not immediate savings.

---

## Part 2 — Auth

**Do this after the app runs end to end locally.** It is not a prerequisite.

### What changes

One file: `app/core/security.py`, specifically `get_current_user`. It
currently decodes a token this app issued. It becomes: validate Supabase's JWT
against their JWKS, then look up or create the local `User` row keyed by the
Supabase user id.

### What does NOT change

Everything that makes this app's authorization interesting stays in your
database:

- `role` (student / instructor / admin) and the `require_instructor` / `require_admin` gates
- `peppercorns`, the ledger, and every debit/refund path
- `status`, `strikes`, suspension
- `subscriptions` and per-language `entitlements.check()`
- `preferred_language`, learning events, the mentor profile

Supabase Auth answers *who is this person*. It does not answer *what may they
do* — that stays yours, because your tier model (per-language, expiry-driven,
Stripe-backed) is custom enough that no provider's role system expresses it
cleanly.

### Migration sketch

1. Add `supabase_user_id` to `users` (nullable, unique, indexed) in a new
   Alembic revision.
2. Replace token decoding in `get_current_user` with JWKS validation. **Cache
   the JWKS** — fetching per request is a latency and rate-limit problem.
3. On first request from a new Supabase id, create the local `User` row and
   grant the signup bonus exactly as `/auth/register` does today.
4. Leave `/auth/me`, `/auth/me/language`, and every other route unchanged.
5. Retire `/auth/register` and `/auth/login`; the frontend uses Supabase's
   client SDK. Keep `hash_password` / `verify_password` only if you support
   existing local accounts during a transition.

### What you gain

The tedious periphery: password reset, email verification, MFA, social login,
login rate limiting, and revocable sessions. That last one matters — your
current JWTs stay valid for 7 days even after suspension, because there is no
revocation list.

### What to watch

- **Do not put tier or role state in Supabase user metadata.** It will drift
  from Stripe and you will get users who paid but cannot access, or cancelled
  but still can. The database is the source of truth.
- Row Level Security is powerful, but your API already enforces ownership in
  every query. Enabling RLS on tables the backend writes with a service key
  adds complexity without adding safety here.
- The service-role key bypasses RLS entirely. Backend `.env` only — never in
  the frontend bundle.

---

## Migration order

1. Run locally on Chroma + local auth. *(where you are now)*
2. Move vectors to pgvector — config change plus a re-ingest.
3. Deploy with real users, still on local auth.
4. Move auth to Supabase once the rest is stable.

Doing 2 and 4 together means that when something breaks you will not know
which half caused it.
