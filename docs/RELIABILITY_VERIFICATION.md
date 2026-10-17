# Reliability work and verification — October 15, 2026

Curriculum organization, subscription packaging and payment decisions remain
with the owner for later. This work changes reliability and verification; it
does not settle those product decisions or declare the entire platform complete.

## Approved uploads and retrieval

- All 38 existing approved PDFs have reference projections accessible through
  the local, language-scoped chat retrieval path. Original extracted text,
  approval status, reviewer, review time, review notes and recorded vector IDs
  were compared to the pre-migration backup and are unchanged.
- Existing upload vectors are excluded from chat and practice-note retrieval.
  They are not blindly marked answer-safe or re-embedded. Paid re-embedding was
  not needed to restore approved reference excerpts.
- Each request checks current database approval and track before selecting a
  projection. Deleted/rejected sources and superseded text cannot regain access
  through stale vectors. Focused lesson chats and explicitly selected framework
  subjects do not mix in unrelated uploads.
- New uploads accept an explicit language; the `/learn` UI supplies a separate
  reference-language selector. Filename conflicts are rejected before indexing.
  Legacy filenames are conservatively inferred. Ambiguous sources remain
  unavailable to learners until their language is supplied.
- Projections stop at answer/exercise/gotcha boundaries and numbered blueprint
  implementation sections. Code blocks, code-like lines and structured answer
  payloads are withheld. New vector chunks use this same projection, with a
  language, projection version, content revision, reference kind,
  `contains_answer=false`, and `verified=false`.
- This filter is conservative and may omit useful prose or fragment PDF tables.
  It is not a semantic proof that arbitrary instructor prose contains no answer.
  Human source review and adversarial live-model evaluation remain necessary.
- Chat returns selected upload filenames, revision hashes and short excerpts;
  the UI displays them as escaped text. These identify retrieved context, not
  proof that every generated statement follows from it. Excerpts are returned
  with the response; historic chat-message rows do not persist citation objects.
- Instructor document responses distinguish approval, reference availability,
  missing language and an empty projection. Approval is not executable-solution
  verification. Publishing does not turn a PDF into a tested workout.

`data/evaluations/uploaded_retrieval.json` contains 38 topic questions with
expected sources/languages. `docs/uploaded-reference-audit.json` records their
source-at-four and wrong-language checks, original source hashes, revision
hashes and approval fingerprints. All 38 currently pass. This is a retrieval
check, not a scored human assessment of answer correctness.

## Durable lifecycle and abandoned requests

Vector deletions are enqueued in `vector_cleanup_jobs` in the same transaction
as replacement, rejection or deletion. Failed provider cleanup retains a job
with an attempt count and exception type for retry. Current database authority
blocks stale-vector access while physical cleanup is pending.

Upload vector IDs are chosen before writes. Partial indexing failures roll back
the attempted publication/replacement and enqueue all prospective IDs for
cleanup, preserving the old approved version. A process crash between external
indexing and persisting its outcome can still leave unreachable orphan vectors;
there is no distributed transaction between SQL and the embedding store.

A maintenance worker runs on startup and then every minute. Each pass settles
up to 100 operations older than 30 minutes and retries up to 20 cleanup jobs.
An atomic terminal-state transition permits one refund of the recorded debit.
Practice lock ownership uses the operation ID, so an old reservation cannot
release a newer action's lock. Demand-driven recovery remains available too.
Database/provider outages delay work until a later successful pass.

Manual admin credits now accept the existing idempotency protocol. Same key and
payload replay the receipt; changed payload returns 409. Existing balances and
prices are not redefined. Legacy clients omitting keys cannot obtain retry
protection. Screening messages now accurately say suspension preserves balance
while disabling spending.

## Execution and workout evidence

All 70 current JavaScript/Java reference implementations pass their curated
suites (422 case checks). The current 23 DSA fixture sets additionally pass
independent oracles using exhaustive search or basic mathematical definitions.
The tests require expected-answer diversity so a constant-return submission
cannot pass an entire current DSA fixture set.

These checks support the tested input domain. They are not proofs for every
possible input. The audit separately reports 333 reference-only catalog items
and 67 non-executable packaged exercises; these are not certified workouts.
Curriculum expansion and structuring remain deferred as requested.

`EXEC_BACKEND=docker` adds optional per-command container isolation using an
operator-provided, digest-pinned `EXEC_CONTAINER_IMAGE`. The image must contain
GNU `timeout`, Python/Node/Java toolchains and any other advertised runtimes.
It runs with no network, a read-only root, dropped capabilities, no new
privileges, process/memory/CPU/file limits, and only a disposable scratch mount.
An in-container wall timer remains effective if the host CLI disconnects.
Container startup errors fail closed; there is no host fallback. Reference
verification caching includes the selected backend and image.

The default `subprocess` mode remains for trusted private development. It cannot
isolate host files or networking. Docker's daemon was unavailable during this
work, so actual container isolation and runtime compatibility have **not** been
certified. Offline tests check command construction, failure handling and the
absence of fallback. `tools/check_container_isolation.py` is the explicit real
container check for file/environment/network/root/process boundaries and
JavaScript/Java execution. Do not describe the Docker path as validated until
that tool passes with the selected image.

## Mentor and complete learner journeys

Recall is available in hints and reviews, restricted to the selected language.
It labels unfinished hint reasoning separately from reflections associated with
an earlier verified solve. Legacy reflections without a prior solve are not
used. Another learner's reasoning and the current problem are excluded.
Cross-language subscription bonuses remain deferred and disabled.

Mentor reference prompts no longer include protected solution sections. Earlier
reasoning, profiles and reference notes are explicitly treated as untrusted
material, not correctness evidence. Obvious code-like mentor output is replaced
with a safe guiding question. This guard cannot guarantee that a live model
will never leak a natural-language solution.

Tests cover all four tiers in JavaScript and Java, reference-answer withholding,
recall provenance, language/owner separation, and code-output suppression.
They mock generation and therefore do not establish live tutoring quality.
`tools/evaluate_mentor.py --live` makes eight provider calls and saves a human
review rubric; it has not been run and makes no approval claim.

HTTP journey tests for **both JavaScript and Java** execute real learner code
through the actual practice graph: fail a submission, request a hint, restore
checkpoints, pass, replay a submission without another charge, explicitly reveal
the solution and reflect. Reflection cannot manufacture a solve. Model output
and external retrieval are stubbed in these tests; execution and persistence
are real.

## Data export, database safety and operational checks

Profile export now uses the authenticated API and downloads JSON. The prior
bare hyperlink omitted the bearer token. Export no longer silently truncates
at 5,000 events; profile-event deletion uses a complete user-scoped bulk delete.
The UI states that saved practice sessions and chat conversations remain.
This action is not complete account erasure. Citation HTML is rendered as text.

`tools/storage_health.py` provides a read-only ledger/integrity audit, a SQLite
online backup and restore to a **new** destination. Destination files are mode
0600 and existing files/symlinks cannot be overwritten. It never auto-corrects a
ledger discrepancy. PostgreSQL requires database-native backup tooling.

Before migrations, a recoverable backup was stored at
`var/backups/before-reliability-20261015.db` (ignored by Git). A restore drill to a
separate temporary database passed integrity and ledger checks with all 38
published records. The live database also reports zero ledger mismatches.
Backups contain private data and need the same access controls as the database.

Migrations 0007 and 0008 add the cleanup outbox and upload language. They have
been applied locally. Startup checks the required table and language column.
Migration/model drift checks pass. The backup predates both migrations; upgrade
a restored copy before starting this version of the application.

## October 15 live follow-up

The earlier Docker/provider limitations below are historical. Actual isolation,
JS/Java references, OpenAI comparison and mentor checks have now run; see
[the follow-up evidence and remaining limits](REMAINING_CHECKS_2026-10-15.md).
The app still defaults to trusted host execution and ordinary RAG.

## Repeatable checks

From `dsa-chatbot-api`:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python tools/check_migration_drift.py
.venv/bin/python tools/audit_uploaded_knowledge.py
.venv/bin/python -m tools.audit_exercises --output docs/exercise-audit.json
.venv/bin/python tools/storage_health.py audit
```

From `dsa-chatbot-ui`:

```sh
npm test
npx tsc --noEmit
npm run build
```

Live container and provider evaluation are separate gates. No public deployment,
paid embedding refresh, subscription purchase or commercial policy change was
performed.

## Verified results for this change

- Backend: **425 tests passed**. The final run reports one dependency deprecation
  warning from LangGraph's serializer; there were no test failures.
- UI: **65 tests passed** in the repository's configured test discovery,
  including export, source rendering, chat state and existing practice tests.
- TypeScript (`tsc --noEmit`), production build, Python compilation and whitespace
  checks passed.
- Fresh SQLite migration upgrade, downgrade to 0006, and re-upgrade passed in a
  temporary database. Model/migration column drift and live schema startup
  checks passed.
- Approved-PDF retrieval: **38/38 topic questions** found their expected source
  within four upload results and excluded it under the other language.
- Executable references: **70 passed**, **0 blocked**, **422 curated case checks**.
- Live SQLite integrity and restored backup integrity: **ok**; **0 ledger
  mismatches**. Original PDF source and approval records were preserved.
- Container command/failure tests were rerun after forcing the container timer
  entrypoint: **6 passed**. Real Docker execution and live-provider pedagogy
  remain unverified as explained above.
