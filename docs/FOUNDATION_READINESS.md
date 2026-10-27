# Foundation and DSA readiness across the whole knowledge base

## Owner clarification — October 15, 2026

The learning foundation must support proficiency and versatility in every language
and framework represented in the knowledge base. Validating this foundation is
a prerequisite to arranging learning paths; curriculum sequencing, subscriptions
and payment packaging remain deferred. JavaScript/Java priority does not limit
knowledge-quality review or imply other languages are ready.

## Verified inventory, not certification

The read-only audit examined **17,804 packaged records**, **8 languages**
and **19 subjects**. These counts combine the canonical Java/JavaScript corpus
with the supplemental reference library; the 38 approved upload PDFs remain in
their separate preserved SQL collection and are not added to these JSONL counts.
The audit found no duplicate/missing IDs, missing language/answer flags, non-scalar
metadata, missing documents/provenance, or explicitly safe exercise/gotcha records
under its mechanical checks. This is not a full answer-leakage or factual review.

| Subject | Records | Candidate exercises in corpus | Authored foundation exercises |
| --- | ---: | ---: | ---: |
| c | 1,369 | 224 | 0 |
| embedded-c | 2,094 | 345 | 0 |
| cpp | 414 | 0 | 0 |
| java | 2,377 | 26 | 12 |
| spring-boot | 3 | 0 | 0 |
| spring-core | 1 | 0 | 0 |
| spring-data | 2 | 0 | 0 |
| spring-mvc | 3 | 0 | 0 |
| spring-security | 1 | 0 | 0 |
| spring-testing | 2 | 0 | 0 |
| javascript | 1,903 | 41 | 12 |
| embedded-python | 1,102 | 198 | 0 |
| python | 397 | 25 | 0 |
| python-django | 708 | 0 | 0 |
| python-fastapi | 708 | 0 | 0 |
| python-flask | 708 | 0 | 0 |
| ruby | 1,179 | 192 | 0 |
| rust | 3,218 | 920 | 0 |
| typescript | 1,615 | 206 | 0 |

Candidate exercise counts do not establish runnable fixtures, correct answers or
distinct learning outcomes. Blueprint references can describe exercises without
providing structured exercise records. Authored foundation exercise counts are
catalog presence only; their execution evidence is recorded in separate audits.

## Concrete readiness gaps

- The runner declares function-test adapters for Python, JavaScript, TypeScript,
  Java, C, C++, Rust, Ruby, Go, and C#, plus stdin/stdout-only adapters for
  additional languages. A declared adapter still depends on the selected runtime
  being installed and on a reference that the harness can execute.
- The shared reference extractor now recognizes the function-test language
  headings. Before this fix, TypeScript's 12 fixture-bearing foundation exercises
  were all blocked because their references could not be loaded; C++ headings
  were also missed because `C++` was interpreted as a regular-expression pattern.
  Both parser gaps now have regression tests.
- Failed reference admission now blocks function-based practice for every
  function-test adapter, rather than only JavaScript and Java. Runtime presence,
  the reference implementation, fixtures, and observed execution must all pass.
- Fixture-bearing 12-stage foundation paths are authored for ten languages.
  The October 27 audit passed all 49 current DSA/algorithm and foundation
  references in Python, JavaScript, TypeScript, Java, C, C++, Rust, and Ruby
  (3,192 fixture checks total). Go and C# each have 49 blocked references solely
  because their runtimes are unavailable in the local toolchain. See the
  [current executable coverage matrix](EXECUTABLE_COVERAGE.md) and full
  [machine-readable audit](exercise-audit.json). This is finite exercise
  evidence, not complete language proficiency or proof for every possible input.
- The six Spring subjects contain only 12 seed records and no structured candidate
  exercises. They cannot support a claim of complete Spring proficiency.
- Framework-specific dependency/version compatibility, project builds, tests,
  persistence, request behavior and security behavior need their own validation.
  A passing language-level function does not validate a framework application;
  Spring currently has only a small seed corpus and no verified project workouts.

## Readiness standard to apply to every subject

1. **Explicit coverage:** maintain language-specific requirements for fundamentals,
   idioms, errors, modules, testing, debugging, reference/value behavior and relevant
   memory/concurrency concerns. Record missing material rather than infer readiness
   from document counts. This is a content checklist, not curriculum sequencing.
2. **DSA competency:** cover collection semantics, complexity, recursion, searching,
   sorting, linked structures, stacks/queues, hashing, trees/heaps/tries, graphs,
   greedy methods, dynamic programming and backtracking, with appropriate problem
   families, boundary cases and explanations of tradeoffs.
3. **Verified practice:** each admitted exercise needs a matching statement, input
   contract, starter code, reference implementation, comparison rules and meaningful
   tests in its language. Use independent oracles/property tests and targeted fuzzing
   where supported. Compile-only checks cannot certify solved problems.
4. **Framework competence:** use pinned, documented supported environments and
   runnable minimal projects with dependency-aware unit/integration tests. Review
   framework-specific behavior rather than treating references as generic DSA.
5. **Editorial grounding:** verify explanations, idioms, runtime qualifiers and
   solution reasoning against appropriate primary sources and execution evidence.
   Keep unsupported claims and stale versions out of verified teaching material.
6. **Learning behavior:** test scoped retrieval, evidence-based reviews, tier fidelity,
   protected solutions and learner practice flows per language. Successful retrieval
   alone is not evidence that an answer teaches the right thing.
7. **Honest admission:** distinguish reference-only, awaiting execution/editorial
   review, blocked and verified material. Readiness is against declared requirements
   and supported versions; finite tests cannot prove every possible program correct.

## Audit boundaries and reproduction

The audit records source-file hashes, structural findings, subject-specific retrieval
probes and topic evidence IDs. Every subject currently has `not_certified` status:
that is an overall readiness status, not a reversal of existing individual JS/Java
execution results. Three retrieval probes per subject check language/subject/answer
flags. They do not grade semantic relevance, completeness or model responses.
Keyword topic matches are review leads only. Missing matches require review; a
perfect keyword match count does not mean a subject is complete. The common topic
scan is especially not a framework-specific completeness checklist.

```sh
.venv/bin/python tools/audit_knowledge_coverage.py --output docs/knowledge-coverage-audit.json
.venv/bin/python -m pytest tests/test_knowledge_coverage_audit.py tests/test_reference_library.py -q
```

No source text, approvals, runtime gates, curriculum sequence, model credentials,
balances or commercial policy were changed. No provider calls or submitted-code
execution occur in this inventory audit. Full cross-language content correctness
and exercise certification remain work to complete; this inventory does not claim
that work is finished.

[Machine-readable findings](knowledge-coverage-audit.json)
