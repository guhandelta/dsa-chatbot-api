# Confirmed fixes for the private learning application

For the October 15 reliability changes and current verification, see
[RELIABILITY_VERIFICATION.md](RELIABILITY_VERIFICATION.md). Earlier test counts
below describe their historical checkpoints.

Pricing, paid feature definitions, and the mentor recall redesign remain deferred.
The configured costs and language subscription gate have not been redesigned.
This document describes implemented behavior, not a declaration that the learning
platform or curriculum is complete.

## Request integrity and refunds

Chat, review, mentor questions, practice actions, and manual subscription grants
accept `Idempotency-Key`. Receipts are scoped to authenticated user and endpoint.
Same key and input replay the terminal result; changed input and in-flight
requests return 409. Legacy callers may omit the key, but cannot obtain transport
retry protection without one. The UI sends and retains keys across network
failures, including page reloads, and retires them after terminal responses.

A per-user database lock serializes preflight/rate-limit/debit decisions. The
receipt and debit commit before expensive work. Feature writes, practice
checkpoints, and the successful receipt commit together. Exceptions roll back
feature writes and refund the reserved amount once. Lookups and final learning
writes are inside this boundary; self-critique failure fails the review rather
than silently returning an incomplete result. Unsupported evidence stages are
reported as unavailable; student test failures are ordinary evaluations.

A process crash leaves a running receipt. After 30 minutes a retry can settle
and refund it without executing it again. Reading an interrupted practice session
also recovers expired reservations and releases its action lock. A late worker
cannot overwrite a terminal receipt. A database outage can delay settlement;
this is durable recovery, not an unconditional instantaneous refund guarantee.

## Connected practice graph

- `POST /practice/sessions` starts a free, authenticated graph session.
- `GET /practice/sessions/{id}` restores only the owner's session.
- `POST /practice/sessions/{id}/actions` accepts submit, hint, reflect, or quit.
- Checkpoints and pending writes use the application database through a custom
  LangGraph saver; in-memory checkpointing is confined to unit tests.
- The practice screen now submits and requests hints through this graph.
- Subscription, screening, suspension, rate-limit, and currency checks remain
  outside replayable graph nodes. Concurrent actions are rejected.
- A passing evaluation offers an optional, free reflection. Submitting another
  attempt starts a new graph session while retaining prior evaluated history.

## Evidence and screening

Java reference extraction and batched differential fuzzing are connected.
Python, JavaScript, and Java can measure median runtime inside the constrained
executor. Explicit supported workload factories produce strictly increasing
sizes; unsupported workloads are not assigned a made-up curve. JVM/JIT noise and
small durations can make measurements inconclusive. No timing result proves a
complexity class. Supported shapes remain primitives and supported arrays;
linked-list/node serialization is still outside the compiled harness contract.

The runner bounds output using file-backed capture and file-size limits, strips
its environment, and terminates the process group on timeout/cleanup. Python
screening also resolves imported aliases through the AST and ignores comments.
Warnings refuse execution without strikes; hard blocks increment strikes
atomically. Replaying a rejected keyed request does not add another strike.
Chat now enforces suspension and a configurable hourly rate limit as well.
These controls improve local execution; they do not constitute an OS security
sandbox or prove that arbitrary code is safe.

## Reflection and instructor data

Reflection requires an existing passed evaluation for the same user, problem,
and language. It creates a separate reflection event and does not manufacture
or duplicate solves. The migration converts legacy solved events containing
reflection text into reflection events; ordinary evaluated solve events remain.
Recall can consume the new event kind, while its selection/tier policy is
otherwise unchanged pending clarification.

Instructor-generated Markdown now retains all test cases, expected outputs,
entry-point names, and execution mode in protected front matter. Publishing and
deletion invalidate catalog and local search caches. Student-safe views strip
these fields. Regression tests publish a generated problem and then execute a
student solution against its reloaded fixtures.

## Subscriptions

Webhook signatures are checked against the raw request body using Stripe v1
HMAC and a 5-minute timestamp tolerance. Event IDs prevent repeated processing;
differing payloads cannot reuse a receipt. Signed subscription state supplies
its own expiry rather than repeatedly adding an assumed 30-day period. Older
events cannot overwrite newer subscription state. Cancellation preserves access
through the recorded expiry; expired/inactive subscriptions do not unlock help.

Checkout and invoice events are acknowledged without inventing pricing or
entitlement periods. Their final commercial mapping is deferred. Manual private
access remains available through the admin grant endpoint, with keyed retry
protection. No payment or external account changes were made.

## Migration and verification

Run `alembic upgrade head` before restarting an older checkout. Migration 0005
adds durable receipts, graph sessions/checkpoints, webhook receipts, and the
subscription event timestamp. Startup rejects missing required service tables.
Migration 0006 adds ownership tokens to practice locks so that a failed or stale
worker cannot release another request's lock. The migration was tested through upgrade, legacy-data conversion, downgrade,
and re-upgrade on a temporary SQLite database. It was then applied to the local
SQLite database after creating a recoverable backup.

Tests cover receipt replay and conflicts, in-flight requests, refund failures,
interrupted-session recovery, reflection ownership, graph restoration, Java
fuzzing/timing, generated fixture round trips, signature rejection, duplicate
webhooks, cancellation expiry, and out-of-order subscription events. Frontend
tests cover graph-backed hints, session restoration, reflection, optional
solution reveal, and network retry keys. Real-provider pedagogy evaluation and
signed-in visual review remain separate work.

Protocol references: [Stripe signatures](https://docs.stripe.com/webhooks/signature),
[LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

Latest automated verification: **327 backend tests** and **59 frontend tests**
passed; TypeScript checks, the frontend build, migration drift checks, and
SQLite migration upgrade/downgrade/re-upgrade checks passed. These results do
not certify live-model tutoring quality or every supported database/runtime.


## Six-week policy and executable content admission (October 14 follow-up)

Hints now use fixed 42-day cycles anchored separately for each learner, problem,
and language. Subscription expiry, cancellation, and renewal preserve the usage
balance. Chat and reviews can spend retained credits; the mentor's existing
language subscription gate remains in force. The profile screen explains this.

Every JavaScript/Java practice start, submission, and solution reveal checks the
reference against at least six distinct fixtures. Failed/incomplete references
block before charging. Instructor publishing now requires JavaScript and Java
and passing execution of every supplied solution; compilation alone cannot pass.
Output comparison is explicit, preserving ordered matrices and boolean types.

The executable audit passed **70 language-specific references / 422 case checks**:
23 DSA problems in both languages plus 12 foundation lessons per language.
Repairs include unsigned Java bit operations, Java word-list arguments, and
actual linked-list node execution. There are **333 reference-only catalog items**
and **67 packaged corpus exercises without executable verification**. These and
complete language-switching pathways remain curriculum work. See
[verification details](CONTENT_VERIFICATION.md) and [machine-readable evidence](exercise-audit.json).

Recall still considers hint notes as well as reflections. Its wording no longer
asserts that every recalled attempt succeeded. Recall sources now have provisional owner approval (including unfinished hints);
cross-language behavior remains an open decision. No learning notes were discarded.
See [product decisions](PRODUCT_DECISIONS.md) for the subscription packaging side note.

Follow-up verification: **349 backend tests / 59 frontend tests passed**.
TypeScript checking, the frontend build, curriculum JSONL validation, migration
drift checks, and the refreshed 70-reference audit also passed. No paid provider
calls were made. These checks do not establish complete curriculum or mentor quality.
