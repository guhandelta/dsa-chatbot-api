# Private JavaScript / Java learning application

See [confirmed integrity fixes and current practice workflow](docs/CONFIRMED_FIXES.md).
See [content admission, six-week hint cycles, and retained credits](docs/CONTENT_VERIFICATION.md)
and the [latest executable reference audit](docs/exercise-audit.json).
See the [language and framework execution coverage matrix](docs/EXECUTABLE_COVERAGE.md)
for verified languages and the next coverage gaps.
Pricing and subscription packaging remain undecided. Recall sources have provisional
approval; cross-language recall remains open. See [product decisions](docs/PRODUCT_DECISIONS.md).

Additional TypeScript, Python, C/C++, Rust, Ruby, embedded and framework references
are now available through Chat's Reference library selector. See
[import coverage, Spring sources and limitations](docs/REFERENCE_LIBRARY.md).

The learning screens now expose a shared 12-stage path in JavaScript and Java,
DSA workouts, and optional solutions gated by completed evaluation. The canonical
curriculum ships with the API and supports local retrieval before vector indexing.

See [release behavior, setup, validation, and remaining work](docs/RELEASE_CURRICULUM.md)
and the [packaged corpus guide](data/curriculum/README.md).

---

# DSA Chatbot API

FastAPI backend: auth (JWT), peppercorn currency with an append-only ledger,
RAG chat over a ChromaDB knowledge base, and structured code analysis.

## Vector store backends

Two options, selected by `VECTOR_STORE` in `.env`:

| Backend | Setup | When |
|---|---|---|
| `chroma` (default) | none | local development |
| `pgvector` | Postgres + `create extension vector` | production; one database for everything |

Both expose the same interface, so every call site works unchanged — the
backend is a config decision, not a rewrite. Switching **requires a re-ingest**
(embeddings live in the store). See `docs/SUPABASE.md`.

## Preflight check

Before starting the server, run:

```bash
python tools/doctor.py           # full check
python tools/doctor.py --quick   # skip the slow execution checks
```

It validates dependencies, `.env` (key presence, JWT strength, admin emails,
gitignore), migration state, language toolchains, content integrity, router
wiring, and runs the three verification tools. Exit 0 means safe to start;
warnings are degraded capabilities, not blockers.

Key *validity* is never checked — that would cost money on every preflight.

## Setup

```bash
cd dsa-chatbot-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: paste your (freshly rotated!) API keys and set JWT_SECRET:
#   python -c "import secrets; print(secrets.token_hex(32))"
```

## Seed the knowledge base (once, and whenever you add problems)

Add one markdown file per problem under `data/dsa_problems/` — the file name
becomes the problem ID (`two-sum.md` → `two-sum`). Then:

```bash
python -m app.services.knowledge_base
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive docs at http://localhost:8000/docs

Startup validates the execution backend. The default is `EXEC_BACKEND=docker`, so
either set a digest-pinned `EXEC_CONTAINER_IMAGE` (and have Docker running), or
for trusted local development set `EXEC_BACKEND=subprocess` in `.env`.

## API overview

| Method | Path | Auth | Cost | Notes |
|---|---|---|---|---|
| POST | /auth/register | – | – | grants SIGNUP_BONUS peppercorns |
| POST | /auth/login | – | – | returns JWT |
| GET | /auth/me | ✓ | – | user + current balance |
| POST | /chat/ | ✓ | CHAT_COST | RAG chat; pass `thread_id` to continue |
| GET | /chat/threads | ✓ | – | list user's conversations |
| GET | /chat/threads/{id}/messages | ✓ | – | conversation history |
| POST | /analyze/ | ✓ | ANALYZE_COST | structured code feedback |

Insufficient balance returns **402** with a message. Provider failures
return **502** and automatically refund the debit (see the `transactions`
ledger table).

## Notes

- DB defaults to SQLite (`dsa_chatbot.db`). Set `DATABASE_URL` to a
  Postgres URL (`postgresql+asyncpg://...` + `pip install asyncpg`) when
  you move off local.
- Schema is owned by Alembic migrations (see below), not by `create_all`.
- Model IDs, costs, and CORS origins are all configured in `.env`.

## Problem catalog

The knowledge base ships with curated Blind 75 problems under
`data/dsa_problems/`, one markdown file per problem. Each contains the
statement, approach, hints, and reference solutions in **Python, JavaScript,
Java, C++, C, and Rust**. The H1 line encodes metadata the catalog parses:

```
# Two Sum (LC 1) — Easy — Array, Hash Map
```

- `GET /problems/` — list (id, title, difficulty, category) for the picker
- `GET /problems/{id}` — full markdown for one problem

Add a problem by dropping in a new `.md` file (same format) and re-running
the ingest command. The analyzer reads the whole reference doc by id, so
feedback is grounded in the canonical solution rather than fuzzy chunks.

## Tests

```bash
pip install -r requirements-dev.txt
pytest                 # ledger, auth, paid chat/analyze flows, catalog
```

Tests use an in-memory SQLite DB and mock the LLM layer, so they need no API
key and make no network calls.

## Offline verification tools (no deps required)

```bash
python tools/check_snippets.py            # syntax-check every solution snippet
python tools/check_python_correctness.py  # run Python references vs known I/O
```


## Training the chatbot (instructors & admins)

Instructors add problems at runtime through `POST /training/submit` (or the
**Train** page in the UI). The pipeline:

1. **Enrich** — an LLM reviews the submission, reports mistakes in the
   statement or code, corrects supplied solutions, writes any missing
   languages, and adds per-solution explanations plus *thinking style* notes
   (the transferable reasoning pattern, for learners taking notes).
2. **Validate** — nothing is trusted. Solutions are actually executed:
   - **Execution:** Python, JavaScript, and supported C/C++/Java/Rust input shapes run against generated cases.
   - **Compile-only fallback:** unsupported compiled-language shapes remain unverified for correctness.
   - **Cross-language agreement:** Tier-1 implementations must produce
     identical outputs — this is what stops the LLM marking its own homework.
3. **Repair** — failures (with real compiler/test output) go back for one
   targeted fix attempt.
4. **Publish** — automatic *only* if all Tier-1 tests pass, implementations
   agree, and every installed Tier-2 toolchain compiles. Otherwise the draft
   is stored as `needs_review` with the full report and never reaches learners.

Published problems are written to `data/dsa_problems/` and **incrementally
upserted** into ChromaDB — no restart, no full re-ingest, and re-training a
problem replaces its chunks instead of duplicating them.

### Roles

| Role | Can |
|---|---|
| student | chat, practice |
| instructor | + submit/delete training problems, upload reference documents for review |
| admin | + assign roles (`/admin/users`), approve/reject document uploads |

Set `ADMIN_EMAILS` in `.env` to bootstrap the first admin; log out and back in
to pick up the role. Admins promote instructors from the Admin page.

### Reference documents (`/learn`)

Instructors can also upload notes and handouts (`.txt`, `.md`, `.pdf`, `.docx`,
`.doc`, up to 10 MB) or paste text, from the **Train** page or the API.
Uploaded text is retrieved for *every* learner's chat, so it is reviewed:

- An **admin's** upload is indexed and published immediately.
- A **instructor's** upload is stored as `pending` and only indexed once an
  admin approves it. Admins can reject with a note, or unpublish later.
- Re-uploading the same filename replaces your earlier version (and sends an
  instructor's document back to review).

| Endpoint | Who | Does |
|---|---|---|
| `POST /learn/train` | instructor, admin | multipart `file` + `track`, or JSON `{text, filename, track}` |
| `GET /learn/documents?status=` | instructor (own), admin (all) | list uploads |
| `GET /learn/documents/{id}` | owner, admin | metadata + text preview |
| `DELETE /learn/documents/{id}` | owner, admin | remove record and vectors |
| `POST /learn/documents/{id}/approve` | admin | index and publish |
| `POST /learn/documents/{id}/reject` | admin | `{note}`; unpublishes if needed |

`track` is `custom` (shared with every track, the default), `dsa`,
`algorithm`, or `language`. Chunks are stored under
`problem_id = "upload:<document id>"`, so an upload can never replace a
curated problem. Run `alembic upgrade head` after pulling this feature.

### Language coverage

`GET /training/status` reports what this machine can verify. Java and Rust
need their toolchains installed:

```bash
brew install openjdk rust     # macOS
```

Without them, those languages are reported as **unverified** — reviewed by the
LLM but not executed. They are never counted as passing.

### Security note on code execution

By default (`EXEC_BACKEND=docker`) submitted code runs in a per-command container
from the digest-pinned `EXEC_CONTAINER_IMAGE` (see "Known limits" under Abuse
prevention). The opt-in `EXEC_BACKEND=subprocess` mode runs on the host with a
wall-clock timeout, CPU/memory/file-size limits, a scratch working directory and
a stripped environment (it cannot read your `.env`). That is appropriate only for
a trusted local setup: it is not a true sandbox, and production refuses it.

## Three learning tracks

Every track has a **Learn** side (RAG chat scoped to that track) and a
**Practice** side (write code, get it executed and reviewed):

| Track | Learn | Practice |
|---|---|---|
| `language` | Syntax, built-in data structures, idioms for the chosen language | Exercises in that language |
| `dsa` | Walkthroughs of original practice problems | Solve in the editor, get structured feedback |
| `algorithm` | The technique, its invariant, and when to reach for it | Tagged problems at Easy → Medium → Hard |

Retrieval is **scoped by track**, so a Python-syntax question never surfaces
graph theory. `focus_id` narrows further to a single item.

### Content metadata

Files may declare front matter; anything without it defaults to `track: dsa`,
so previously authored problems keep working:

```
---
track: algorithm
difficulty: Medium
language: python        # only for track=language
algorithms: binary-search, two-pointers
source: authored        # authored | hackerrank | legacy-leetcode (retired label)
io_mode: function       # function | stdio (HackerRank reads stdin)
---
```

`algorithms` tags are what link an algorithm concept to the problems that
practise it (`GET /tracks/algorithms/{tag}/practice`).

### Language preference

`PATCH /auth/me/language` saves the learner's language; every track and mode
respects it.

### HackerRank-style problems

Set `io_mode: stdio` and the runner feeds each test case to stdin and compares
printed output instead of calling a function.

## Brute-force verification

```bash
python tools/brute_force_check.py
```

Exercises 15,000 catalog filter combinations, 100 randomized correctness cases,
malformed/adversarial content files, and hostile code submissions (infinite
loops, huge allocations, environment reads).


## Execution-grounded review

`/analyze` no longer guesses whether a submission is correct. When the problem
has verified test cases (22 of 23 do — see below), the student's code is
executed against them and the real pass/fail results are fed into the review.
Feedback becomes *"your solution fails on `[3,3], target=6` because you check
the map before inserting"* rather than *"this looks like it might have a bug"*.

Problems without JSON-expressible inputs (linked lists) have no cases; those
fall back to review-only and the prompt explicitly forbids claiming the code
was tested.

### Regenerating test cases

```bash
python tools/backfill_test_cases.py          # dry run
python tools/backfill_test_cases.py --write  # write to front matter
```

No LLM involved: inputs are hand-authored, expected values are computed by the
verified Python reference and independently cross-checked against the
JavaScript reference. A case is only written if both agree.

## Abuse prevention

Student code is untrusted. Defences, outermost first:

1. **Account status** — suspended accounts are refused before anything runs.
2. **Static screener** (`code_screener.py`) — blocks network, subprocess,
   environment, filesystem, introspection, and dynamic-execution patterns
   across all six languages *before* any process is spawned. Verified at
   16/16 malicious samples blocked, 0/13 false positives on real solutions.
3. **Three-strike policy** — a hard `block` records a strike. Strikes 1 and 2
   warn; strike 3 suspends the account and remaining peppercorns are **not**
   refunded. A `warn` verdict (accidental infinite loop, stray `eval`) refuses
   the run but never counts toward suspension — wrongly suspending a paying
   learner costs far more than letting an ambiguous submission reach a sandbox
   that already assumes hostility.
4. **Sandbox** — wall-clock timeout, memory cap, no core dumps, own process
   group (`setsid`), scratch cwd, stripped environment, capped output.
5. **Audit trail** — every blocked submission is written to `security_events`
   and reviewable at `GET /admin/security-events`. Admins can reverse a
   suspension with `POST /admin/users/{id}/reinstate`; the event history is
   retained deliberately.

Blocked submissions are refused *before* the debit, so a student is never
charged for a rejected run — except at suspension, where the balance is
forfeit by policy.

### Known limits

- Docker is the default execution backend. Set `APP_ENV=production`,
  `EXEC_BACKEND=docker`, and `EXEC_CONTAINER_IMAGE=your-image@sha256:<64 hex digits>`
  in the deployment environment. Install Docker and preload the pinned image
  with the supported toolchains; execution never pulls images automatically.
  Startup rejects production subprocess mode, missing/unpinned images, and a
  missing Docker CLI. Docker runtime failures refuse execution without fallback.
- Docker runs use network isolation, a read-only root, a non-root user, dropped
  capabilities, and per-container memory/process limits. Only scratch is mounted.
- Trusted local development can explicitly set `APP_ENV=development` and
  `EXEC_BACKEND=subprocess`. Host mode cannot isolate files or network access;
  never use it for untrusted submissions.
- A static screener is defence in depth, never the boundary. Treat `allow` as
  "nothing obvious found", not "this code is safe".


## Precision review pipeline

`/analyze` gathers evidence before it reasons. Speed is deliberately not the
priority — correctness of the verdict is.

1. **Curated cases** — the problem's verified test cases.
2. **Differential fuzzing** — 200 generated inputs run against BOTH the
   student's code and the verified reference solution, then diffed. Failing
   inputs are *shrunk* to a minimal counterexample that still respects the
   problem's stated constraints.
3. **Complexity measurement** — the submission is timed across growing inputs
   and the growth exponent fitted. Reported as an observation, never a proof.
4. **Review** — the LLM writes feedback with all of the above as input.
5. **Self-critique** — a second pass audits every claim against the evidence
   and deletes anything unsupported.

Stage 5 exists because the worst failure mode is a confidently hallucinated
bug in correct code. Measured behaviour: 5/5 real student bugs caught with
minimal counterexamples, 12/12 correct solutions passing with zero false
accusations.

The response includes the full `evidence` object, so feedback is auditable
rather than taken on faith. Claims backed by a failing input are facts; style
and approach suggestions are opinions, and the prompt requires them to be
phrased differently.


## Socratic mentor

`POST /mentor/ask` requires the learner to state their reasoning first — that
is the pedagogy, not a formality. The mentor responds to *their* thinking.

Four hint tiers, escalating only when the learner asks again. **No tier ever
reveals the solution or the literal next step.**

| Tier | Name | What it does |
|---|---|---|
| 1 | Orient | A question surfacing a property of the input they have not considered |
| 2 | Probe the gap | Quotes their own reasoning back and asks what breaks |
| 3 | Recall their own thinking | Reminds them how they reasoned through a similar problem before |
| 4 | Name the shape | Names the technique *family* and asks how they would set it up |

Tier 3 is the distinctive one: `recall_similar_moment()` searches the
learner's own recorded reasoning for a structurally similar problem and
reminds them that they already know how to think this way.

At tier 4 with no answer available, the mentor offers to **step back** — an
easier problem on the same pattern, or the concept page. Refusing to help and
refusing to redirect is how learners give up.

## Learning pattern tracking

Everything stored is **observable behaviour**: submissions, the exact inputs
they failed on, algorithm tags, hint tiers reached. Error categories are
derived deterministically from the fuzzer's counterexamples — not from a
model's opinion — so the profile is factual.

Nothing infers traits, learner types, or personality. "You have missed the
empty-input case in four problems" is accurate and actionable; "you are a
careless thinker" is unreliable and demoralising. A pattern is only surfaced
after it has recurred at least twice, so one bad day is never presented as a
tendency.

`GET /mentor/profile` (learner's own view), `GET /mentor/profile/export`
(full export), `DELETE /mentor/profile` (erase).

## Subscriptions

Student learning access is scoped to the languages covered by active
subscriptions, including fundamentals, chat, reviews, practice and mentoring.
Admins access all available languages; instructors access teaching assignments
and languages associated with their saved uploads. Peppercorns pay for usage
within permitted languages and remain on the account after subscription expiry.

### Payments

**No card data reaches this server.** Checkout runs in Stripe Checkout, hosted
by Stripe; Stripe then calls `POST /subscriptions/webhook`, which grants or
revokes the entitlement. Only the Stripe subscription id is stored.

The webhook verifies Stripe v1 signatures against the raw body, rejects stale
signatures, and records event IDs for replay protection. Signed subscription
state supplies its expiry. Checkout/invoice pricing mappings remain deferred;
manual admin grants support private development. See
[confirmed fixes](docs/CONFIRMED_FIXES.md) for the current contract.

Renewals extend an existing entitlement rather than stacking duplicates, and
cancellation keeps time already paid for.

## Connected flow (what the UI walks)

```
submit → screen → debit → curated tests → differential fuzz → complexity
       → LLM review → self-critique → record learning event
                                          ↓
                            profile pattern (after 2+ occurrences)
                                          ↓
                        mentor tier-3 recalls their own earlier reasoning
```

`tests/test_integration_flow.py` exercises this with the LLM stubbed and
everything else real. It exists because of a wiring gap it would have caught:
`/analyze` originally never wrote learning events, so the profile stayed
permanently empty and tier-3 recall could never fire.

`POST /mentor/reflect` lets a learner record how they reasoned through a
problem they solved. It is deliberately free — that text is the raw material
tier-3 recall draws on, so charging for it would starve the feature.


## Database migrations

The schema is owned by Alembic. The app **refuses to start** against an
unmigrated database rather than silently calling `create_all` — otherwise the
running schema quietly diverges from the migration history and the first real
deployment is the thing that discovers it.

```bash
alembic upgrade head          # apply migrations (run before first start)
alembic revision -m "add x"   # create a new revision after changing models
alembic downgrade -1          # roll back one
```

Existing local databases predating migrations should be deleted once:

```bash
rm dsa_chatbot.db && alembic upgrade head
```

Migrations use `render_as_batch=True`, which SQLite needs in order to alter
columns at all. `DATABASE_URL` async drivers are translated to their sync
equivalents automatically in `alembic/env.py`.

### Drift checking

```bash
python tools/check_migration_drift.py
```

Compares every ORM column against the migrations and exits non-zero on
mismatch. Worth running in CI — a migration that diverges from the models is
worse than no migration, because it fails on deploy rather than in dev.


## Observability

Every review and mentor request emits a **trace**: a tree of timed spans with
attributes, token usage, and estimated cost. Without it, "the review felt
slow" and "the mentor gave a bad hint" are unanswerable — there is no way to
see which of the five stages burned the time or what it cost.

No external collector is required. Spans live in memory during a request and
are written to `trace_records` as one row at the end.

### What is instrumented

| Span | Attributes |
|---|---|
| `gather_evidence` | wraps the three verification stages |
| `curated_tests` | case count, passed/total |
| `differential_fuzz` | iterations, passed/total, counterexamples, seed |
| `complexity` | measured, estimate |
| `llm_review` | provider, estimated prompt tokens |
| `self_critique` | **changed** — whether the audit altered the draft, plus mistake counts before/after |
| `recall_lookup` (mentor) | whether earlier reasoning was found |
| `llm_mentor` | provider, tier |

The `self_critique.changed` flag is the most useful single signal in here: it
tells you whether that stage is earning its cost or silently passing drafts
through unchanged.

### Endpoints (admin)

```
GET    /admin/traces?name=analyze&status=error   recent traces
GET    /admin/traces/summary                     aggregates + stage breakdown
GET    /admin/traces/{trace_id}                  full span tree
DELETE /admin/traces?older_than_days=14          prune
```

`/admin/traces/summary` gives count, error rate, avg and p95 latency, average
cost, and average ms per stage — sorted slowest first, which is the "why is
this slow?" answer.

### Guarantees

1. **Tracing never breaks a request.** Exporter and persistence failures are
   logged and swallowed. An observability bug must not cause an outage.
2. **Nothing sensitive is stored.** Key-shaped attributes (`api_key`,
   `password`, `user_code`, `reasoning`, `message`) are redacted at every
   nesting level, and free text is truncated. Traces are long-lived debugging
   data; secrets and full student submissions do not belong in them.
3. **Async-safe.** The active trace is a `ContextVar`, so concurrent requests
   never interleave spans.

### Forwarding elsewhere

```python
from app.services.tracing import register_exporter
register_exporter(lambda t: my_collector.send(t.to_dict()))
```

Exporters run inline on request teardown, so keep them fast — anything slow
should enqueue and return. This is the seam for Phoenix or OpenTelemetry;
instrumentation does not change.

### Retention

Traces accumulate quickly. Pruning is manual (`DELETE /admin/traces`) so the
policy is an explicit operator decision rather than a silent default.


### Private agentic retrieval pilot

Ordinary RAG remains the default. An admin-only opt-in experiment is available
with `AGENTIC_RAG_ENABLED=true`; see
[the measured results, limits and remaining risks](docs/AGENTIC_RAG_EXPERIMENT.md).
The experiment does not certify teaching accuracy or change subscription/pricing
policy. Keep it disabled outside controlled evaluation.

October 15 follow-up: [OpenAI comparison, live mentor and Docker checks](docs/REMAINING_CHECKS_2026-10-15.md).

[Whole-library foundation readiness and coverage audit](docs/FOUNDATION_READINESS.md) covers every packaged language and framework subject.

[October 16 knowledge-base gaps and language suggestions](docs/KNOWLEDGE_BASE_GAPS_2026-10-16.md) · [HTML/CSS training-data generation prompts](docs/training-prompts/README.md).

## Role and language access

Admins can learn in every available language. Instructors can learn in their
assigned teaching languages and languages associated with their saved uploads.
Students require active subscriptions covering their chosen languages. Both
instructors and admins retain RAG training access. Access is enforced by the API
as well as filtered selectors, including for saved sessions and receipt retries.

Run `alembic upgrade head` for migration `0009_language_access`. Assign instructor
languages from Admin, then use Chat's language/reference selectors to browse
permitted material. See [the full access contract](docs/ROLE_LANGUAGE_ACCESS.md)
for expiry, instructor upload provenance and older chat history behavior.


## Language integrity and subscription audit

Run the offline content audit after editing exercises, examples, or course sources:

```bash
.venv/bin/python tools/audit_language_integrity.py
.venv/bin/pytest tests/test_language_integrity.py tests/test_language_access.py
```

The audit checks all released quiz banks, distinctive snippet syntax, starter
code, path/pool assignments, source language metadata, and selected-language
learner views. Subscription tests exercise all twelve supported language scopes,
unauthorized API calls, and saved quizzes/comparisons after expiry. Multiple
active subscriptions permit their respective languages; a saved preference or
URL never grants access. Static checks do not prove arbitrary code semantics or
live model response accuracy.


## Debugging challenge library

Study Room → Debug with Me now offers 1,982 debugging and code investigation problems across all 28
current language/framework subjects, with Easy, Medium, Hard, Expert and Extreme
choices. Each subject has at least two distinct problems per difficulty. The
subject chooser is scoped to the selected language and checked against the
student's active subscription by the API.

Assignments are stored per learner in `debug_challenge_attempts`. Refreshing
resumes the current assignment; asking for the next problem reserves an unseen
one. Skipped and reviewed assignments remain in history, including across
sessions and devices. Exhaustion never silently resets the pool. Review saves
the student's diagnosis and regression-test proposal; it does not execute code,
award mastery, or claim automatic test success. Existing bring-your-own-code
Socratic debugging remains available.

Deployments must run `.venv/bin/alembic upgrade head` to install migration
`0016_debug_challenges` before starting the updated API. The local SQLite
migration has already been applied for this workspace.

To audit or extend the authored cases:

```bash
.venv/bin/python tools/build_debug_challenges.py
.venv/bin/python tools/compile_debug_knowledge.py
.venv/bin/python tools/audit_debug_challenges.py
.venv/bin/pytest tests/test_debug_challenges.py
```

The bank includes 207 new authored scenarios, 434 existing authored quiz code investigations,
and 1,341 reference bad/good example pairs after code deduplication.
Only the code under investigation and the problem brief are sent to students
or the debug coach; corrected examples/QA diagnoses remain server-side. Reference-derived
cases are reasoning material and are not represented as independently executed
or hardware-verified tests.


## Roles of the Study Room modes

| Mode | Purpose and contents |
|---|---|
| Explain | Understand the selected concept through its mental model, one small correct worked example, follow-up questions, a pitfall, and a saved takeaway. Optional reflection prompts are ungraded. |
| Debug with Me | Investigate a bug or trace output/state changes in code tied to the current topic. The coach guides the learner’s diagnosis; correct trace snippets are not falsely described as buggy. |
| JavaScript vs TypeScript | Same-topic reference for this pair only: runtime behavior, static types, narrowing and migration traps. Both subscriptions are required; UI and API enforce the pair restriction. |
| What next? | Separate charts for path mastery, unique DSA solves and debugging self-review; Design Patterns explicitly marks its assessed pathway as coming soon. Also recommends one activity and shows weak spots, recent responses and notes. |

Reflection questions are shown only in Explain. Sending a message does not mark
an exercise complete or unlock a stage. Progress comes from the backend's graded
checks and exercise results.

Debug requests carry the resolved selected/current path topic, even when the
URL has no explicit focus. The server filters candidates, progress counts and
resumable assignments to that topic. An omitted API focus uses the learner's
current topic. Framework collection context is retained when moving from Open
chat into the other modes. A missing/exhausted difficulty never substitutes an
unrelated topic. All 180 core path nodes have at least one relevant investigation;
not every introductory topic needs every advanced difficulty level.

The runtime debugging KB is `data/debug/knowledge-base.json`, separate from quiz and
reference retrieval. `tools/compile_debug_knowledge.py` is an explicit offline publishing
step. Changes to quiz/reference sources do not silently enter live debugging sessions.
Missing topic/difficulty content shows **Coming soon**; exhausted pools have a distinct
message. See [the debugging authoring guide](data/debug/README.md).

Explain adds a per-topic pathway: lesson and worked example → reflection → graded
checks → application → related debugging/review. Reflection/reading do not earn mastery.
The progress overview is a free deterministic `GET /study/progress-overview?language=...`
endpoint scoped to the authenticated user and subscribed language. It never invokes a model.
Charts use different denominators; there is no combined mastery percentage. Design Patterns
has reference lessons, but a graded pathway and progress tracking are still to be built.
See [the product and cost roadmap](reports/study-progress-2026-10-22/ROADMAP.md).


## Tiered Explain pilot and personal study tips

JavaScript Explain now offers 29 authored units across three tiers: basic structures
(8), combined structures (14), and easy-to-medium DSA (7). Each has a mental model,
a verified worked example, an applied prompt, a pitfall and a DSA bridge. Existing
foundation checks/exercises are linked where appropriate. New combined-topic
assessment is explicitly coming soon; reading or solving a linked foundation
exercise does not certify a whole tier. Other languages retain their current
Explain paths while the tiered version awaits language-specific review.

`GET /study/explain-pathway?language=javascript` is subscription-scoped and free;
`explain:javascript:<slug>` is the stable lesson/coaching focus. What next includes
separate focus/honing and strengths/extension sections from completed quiz answers
and unique recorded DSA solves. They use deterministic rules, require evidence,
and do not invoke a model. Dedicated debugging cases can be tagged with optional
`explain_unit_ids`; empty combined-topic banks show Coming soon without broadening
into another topic. See [the JavaScript tier plan](reports/explain-tiers-2026-10-22/PLAN.md).

The deeper Explain edition adds 180 guided activities: 12 per basic structure
(8 core, 3 extensions and 1 deliberate review), 4 per combined unit and 4 per DSA
unit. Activities have stable IDs, family IDs, routes, forms, prompts and checklists;
selecting one pins the coach to that exact activity. These are ungraded activities,
not new automatically validated coding problems. Canonical DSA practice IDs and
existing mastery totals are preserved. `tools/deepen_js_explain.py` rebuilds this
static authored bank without model calls.

Use [the reusable curriculum blueprint](docs/curriculum/BLUEPRINT.md),
[the unit authoring template](docs/curriculum/UNIT_TEMPLATE.md), and
[the JSON unit template](docs/curriculum/unit-template.json) when crafting language
or framework profiles. Frameworks should adapt the last tier to independent
integration/design practice where a DSA endpoint does not fit.

Review activities are manually accessible today; automatic review scheduling is not yet implemented.
