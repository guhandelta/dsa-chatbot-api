# Executable language and framework coverage

Updated October 27, 2026 from `tools.audit_exercises` using trusted local
runtimes and the pinned Docker sandbox. Go and C# were rerun in Docker after
their runtimes were restored. This is execution evidence for the repository's
authored fixtures, not a claim of universal correctness or full
language/framework proficiency.

## Function-based curriculum audit

The current audit covers 37 DSA/algorithm references and 12 language-foundation
exercises per language. Each exercise is checked against its own fixture set;
the full report records source hashes, case counts, outcomes, and blockers in
[`exercise-audit.json`](exercise-audit.json).

| Language | Verified | Blocked | Fixture checks | Local result |
| --- | ---: | ---: | ---: | --- |
| Python | 49 | 0 | 399 | Verified |
| JavaScript | 49 | 0 | 399 | Verified |
| TypeScript | 49 | 0 | 399 | Verified |
| Java | 49 | 0 | 399 | Verified |
| C | 49 | 0 | 399 | Verified |
| C++ | 49 | 0 | 399 | Verified |
| Rust | 49 | 0 | 399 | Verified |
| Ruby | 49 | 0 | 399 | Verified |
| Go | 49 | 0 | 399 | Verified in Docker |
| C# | 49 | 0 | 399 | Verified in Docker |

The ten verified languages total 490 references and 3,990 fixture checks. A
source file, adapter declaration, compile-only result, or old audit does not
count as a pass. The Go and C# rows in [`exercise-audit.json`](exercise-audit.json)
record the Docker image digest used for their rerun.

The learner preflight now enforces a passing executable reference for every
function-test language. Missing runtimes, references, or valid fixtures block
the exercise before learner code is evaluated or charged. Languages with only
stdin/stdout adapters are not treated as function-tested by this gate.

## Remaining language work

PHP, Dart, Kotlin, Swift, Scala, and Haskell now have function-test adapters.
The five newly covered runtimes use generated typed harnesses and have Docker
integration tests for scalar and one-dimensional array arguments, wrong-answer
detection, and explicit refusal of unsupported nested argument shapes. This
does not yet mean their authored curriculum is verified: each exercise still
needs a curated reference implementation, fixtures, and a passing audit run.
The current 49-exercise audit remains limited to the ten languages listed above.

Fixture verification is finite evidence. Broaden coverage with independent
small-input oracles, property tests and seeded fuzzing where the value types and
problem contracts support them. Review explanations, language-specific edge
cases and source provenance separately from execution.

## Framework work is separate

Spring, Django, Flask, FastAPI, Laravel, Rails, React, Angular, and other
framework content cannot be certified by a language-level function runner.
Framework verification needs pinned dependency versions and runnable project
templates with the relevant build, unit/integration, persistence, routing,
accessibility, and security checks. Keep framework reference material
retrievable, but label it separately from verified projects until those checks
exist. Mobile and circuit emulation remain outside this coverage target for the
initial release.

## Reproduce

From `dsa-chatbot-api`, run an individual language batch:

```sh
EXEC_BACKEND=subprocess PYTHONPATH=. .venv/bin/python -m tools.audit_exercises \
  --language typescript --output /tmp/typescript-audit.json
```

Use `--language go` or `--language csharp` in the configured Docker environment
to verify those runtimes. Run without `--language` for the complete matrix; a
nonzero exit means one or more references remain blocked. Subprocess mode is
appropriate only when auditing trusted repository reference solutions. The API
must continue using its configured isolation policy for learner-submitted code.
