# Executable language and framework coverage

Updated October 27, 2026 from `tools.audit_exercises` using locally installed
trusted runtimes in subprocess mode. This is execution evidence for the
repository's authored fixtures, not a claim of universal correctness or full
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
| Go | 0 | 49 | 0 | Blocked: Go runtime unavailable locally |
| C# | 0 | 49 | 0 | Blocked: .NET runtime unavailable locally |

The eight verified languages total 392 references and 3,192 fixture checks. Go
and C# already have authored exercises and runner adapters; they need a working
runtime in the selected executor and a successful rerun before they can be
certified. A source file, adapter declaration, compile-only result, or old audit
does not count as a pass.

The learner preflight now enforces a passing executable reference for every
function-test language. Missing runtimes, references, or valid fixtures block
the exercise before learner code is evaluated or charged. Languages with only
stdin/stdout adapters are not treated as function-tested by this gate.

## Remaining language work

PHP, Dart, Kotlin, Swift, Scala, and Haskell have stdin/stdout execution
adapters but not function-test adapters for the current function-shaped exercise
catalog. Their learning material and compiler/runtime presence do not establish
verified DSA coverage. They need explicit exercise contracts, suitable harnesses,
curated fixtures, and independent edge-case/oracle checks before they join the
same admission tier. The Go and C# path should be rerun inside the pinned
container image after runtime probes succeed.

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
appropriate here only because the audit executes trusted repository reference
solutions. The API must continue using its configured isolation policy for
learner-submitted code.
