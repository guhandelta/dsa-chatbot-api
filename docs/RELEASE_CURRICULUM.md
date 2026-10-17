# JavaScript / Java learning foundation

For subsequent fixes and the connected graph workflow, see [confirmed fixes](CONFIRMED_FIXES.md).

The first release has two entry points: a shared language curriculum and DSA
workouts. Learners can begin at any stage; prerequisite links communicate the
suggested order without blocking experienced learners. Progress records passed
exercise evaluations per user and language. A test pass is a checkpoint, not
proof of conceptual mastery.

## Delivered

- 12 stages per language: values, conditions, loops, functions, strings,
  arrays, maps, sets, objects, validation, recursion, and complexity / DSA.
- 24 executable foundation exercises with 144 reference checks, plus the
  existing DSA catalog. Supplemental concepts come from the canonical
  4,280-record Java/JavaScript JSONL export bundled with the API.
- Java submissions use the existing compiled execution harness through the
  review pipeline. A macOS javac shim without a real JDK is unavailable.
- Lessons render their worked examples and starter code. Reference-only
  pages never advertise an executable exercise.
- Learning navigation exposes JavaScript, Java, Language Fundamentals, and
  DSA. Other legacy content is retained for later releases.

## Solution access

Both `/problems/{id}` and `/tracks/items/{id}` return learner-safe text without
front matter, hidden tests, approach, hints, or reference solutions. Instructor
training endpoints remain privileged authoring interfaces.

A successful `/analyze/` request with a completed executable test evaluation
records an `evaluated` learning event. Passing and failing evaluations unlock
access; missing runtimes, compile-only checks, provider failures, and blocked
submissions do not. Existing review history is not retroactively assumed to
be executable evidence. A learner must resubmit older work to establish access.

`GET /problems/{id}/solution-access?language=java` reports access without an
answer. `GET /problems/{id}/solution?language=java` checks authenticated user,
problem, and language before returning only that language's solution. The
frontend calls it only after clicking **Reveal solution**. Reloading restores
access, not visibility. Switching problems/languages resets the displayed answer.

Chat and review prompts prohibit complete exercise solutions; mentor prompts
retain their Socratic rules. These are model instructions, not a mathematical
guarantee against every possible generated spoiler. Canonical solutions are
protected independently through API access control.

## Retrieval and indexing

BM25 retrieves current learner-safe lessons and packaged curriculum locally,
scoped by language, track, and optional focus. It works before vector indexing
and when the embedding provider is down. Vector results supplement it using
`contains_answer=false`, track, and language filters. Errors never trigger an
unfiltered search. Focused retrieval does not broaden to unrelated topics.

To refresh vectors with the configured real embedding provider:

```sh
.venv/bin/python -m app.services.knowledge_base
```

This can incur embedding-provider charges and rate limits. It is optional for
local curriculum retrieval. The refresh replaces only `catalog=release-v1`
vectors and preserves instructor uploads. Old unlabelled vectors are excluded
from learner chat until refreshed. Avoid changing the embedding model in an
existing collection: use a fresh store / reindex for a different model.
Fake embeddings require explicit `EMBEDDING_PROVIDER=deterministic` and are
for development only; unavailable providers no longer silently select them.

## Validation

```sh
.venv/bin/python tools/validate_curriculum.py
.venv/bin/python -m pytest -q
.venv/bin/python tools/check_migration_drift.py
```

From the UI directory:

```sh
npm test
npx tsc --noEmit
npm run build
```

## Remaining application work

- Expand each concept's exercise coverage and add broader DSA difficulty /
  pattern coverage. The original DSA catalog has 23 problems, with executable
  fixtures for 22; linked-list serialization is still unsupported there.
- Review source attribution, unverified supplemental snippets, and curriculum
  accuracy with instructors. Twelve stages establish a starter path, not a
  complete Java or JavaScript course.
- Run a human tutoring evaluation with real providers for explanation quality,
  hint usefulness, factual grounding, and spoiler resistance. Automated model
  tests use stubs; no paid LLM/embedding calls were made for this change.
- Replace the existing subprocess executor with a real sandbox before running
  untrusted code in a public deployment. Static screening is not isolation.
- TypeScript, embedded systems, frameworks, and design patterns are deferred.

Evaluation access uses the existing learning-event table. Subsequent request and
practice integrity fixes require migration 0005; see the confirmed-fixes guide.
Local JDK configuration is machine-specific.
