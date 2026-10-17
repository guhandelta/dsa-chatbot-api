# Knowledge-base gaps, additions and deferred web plans

Assessment date: October 16, 2026.

## What this report establishes

The refreshed inventory covers **17,804 packaged records, eight languages and
19 subjects**, plus separate evidence from the authored catalog and the prior
38-document approved-upload audit. All eight languages are in scope: C, C++, Java,
JavaScript, Python, Ruby, Rust and TypeScript. These are imported/reference records,
not model fine-tuning or counts of verified lessons. The 38 uploaded PDFs are not
added again to the packaged-record total.

This report consolidates **all currently evidenced gaps and outstanding review
categories**. It cannot truthfully enumerate every factual error or omitted topic
before a record-by-record editorial and competency review. Unknowns remain explicit;
passing structural checks does not convert them into confirmed completeness.

Sources of local evidence: [whole-library audit](knowledge-coverage-audit.json),
[foundation readiness](FOUNDATION_READINESS.md),
[reference import](REFERENCE_LIBRARY.md),
[execution/admission rules](CONTENT_VERIFICATION.md), and
[latest live and container findings](REMAINING_CHECKS_2026-10-15.md).

## Subject-by-subject gaps

| Subject | Records | Candidate exercises | Confirmed missing or unverified readiness |
| --- | ---: | ---: | --- |
| c | 1,369 | 224 | 224 candidate exercises; no authored fixture-bearing foundation lessons; complete C DSA execution audit and admission parity are absent. |
| embedded-c | 2,094 | 345 | Hardware/board/toolchain assumptions and behavior are unverified; 345 candidates have no complete hardware/simulation certification. |
| cpp | 414 | 0 | No structured exercise records in this imported subject; 23 authored C++ DSA solution sections exist separately but are not fully certified. |
| java | 2,377 | 26 | 12 authored foundation lessons and 23 DSA references passed; corpus candidates and broad language coverage are not comprehensively certified. |
| spring-boot | 3 | 0 | Three seed references; no structured exercises or verified configuration/auto-configuration/application projects. |
| spring-core | 1 | 0 | One seed reference; no structured exercises or verified IoC/lifecycle/configuration projects. |
| spring-data | 2 | 0 | Two seed references; no structured exercises or verified persistence/transaction/query projects. |
| spring-mvc | 3 | 0 | Three seed references; no structured exercises or verified controller/binding/validation/error-handling projects. |
| spring-security | 1 | 0 | One seed reference; no structured exercises or verified authentication/authorization/filter-chain/security tests. |
| spring-testing | 2 | 0 | Two seed references; no structured exercises or verified test-slice/integration examples. |
| javascript | 1,903 | 41 | 12 authored foundation lessons and 23 DSA references passed; corpus candidates and broad language coverage are not comprehensively certified. |
| embedded-python | 1,102 | 198 | MicroPython/CircuitPython/runtime/board distinctions need review; 198 candidates have no complete hardware/simulation certification. |
| python | 397 | 25 | 25 candidate exercises and 23 authored DSA solution sections; no authored fixture-bearing foundation lessons or equivalent admission gate. |
| python-django | 708 | 0 | No structured exercise records in this subject; projects, dependencies, migrations, ORM, request/security and integration checks remain unverified. |
| python-fastapi | 708 | 0 | No structured exercise records in this subject; request/response validation, dependencies, async behavior and integration checks remain unverified. |
| python-flask | 708 | 0 | No structured exercise records in this subject; contexts, routing, configuration, sessions and integration checks remain unverified. |
| ruby | 1,179 | 192 | 192 candidate exercises; no runner adapter or authored fixture-bearing foundation lessons. |
| rust | 3,218 | 920 | 920 candidate exercises; runner exists, but complete reference extraction/admission and authored foundation lessons are missing. |
| typescript | 1,615 | 206 | 206 candidate exercises; no TypeScript runner adapter or authored fixture-bearing foundation lessons. |

Candidate counts refer to structured `exercise` records. A zero does not prove
that no blueprint discusses practice; a positive number does not prove executable
fixtures or correct answers exist. Projects listed as unverified are review
requirements, not assertions that every related explanation is absent.

## Cross-language gaps

1. **Coverage has no complete signed-off competency map.** Foundational syntax,
   values/types, functions, modules, errors, strings/Unicode, equality/ordering,
   memory/reference behavior, files/I/O, tooling, testing/debugging and applicable
   concurrency/async concepts need language-specific requirements and evidence.
   Existing document counts cannot establish balanced beginner-to-advanced coverage.
2. **Foundation practice is uneven.** Only Java/JavaScript have authored, fixture-
   bearing foundation sets (12 each). That does not mean their entire fundamentals
   are complete; the remaining six languages need equivalent verified practice.
3. **DSA practice breadth is limited.** The authored catalog has 23 problems,
   concentrated in arrays/hashing, search, DP, bit operations and one linked-list
   reversal. It has no authored graph/trie/heap/tree exercise set. There are 55
   algorithm concept pages and imported candidates, but those do not substitute for
   executable workouts. Expand verified families, variants, difficulty and transfer
   tasks; preserve independent expected results and input contracts per language.
4. **Execution coverage and admission differ.** The runner supports six languages;
   shared reference extraction supports only Python/JavaScript/Java; the learner
   preflight reference gate covers only JavaScript/Java. Ruby/TypeScript are not
   executable practice languages yet. C/C++/Rust compilation/smoke checks do not
   certify their full DSA references. Node-based adapters cover JS/Java/Python only.
5. **Fuzzing/timing parity is incomplete.** Neither currently covers every problem,
   language, signature or data structure. Timing is noisy evidence, not proof of
   complexity. Reference-versus-itself comparisons need independent oracles and
   known-bad variants to avoid circular correctness claims.
6. **Candidate solutions and tests are unverified.** Existing correct publication
   mechanics do not retroactively certify imported exercise payloads. Check
   statements, starter signatures, fixtures, expected results, constraints, numeric
   overflow, ordering/multiplicity, mutation, object identity and nondeterminism.
7. **Version/environment evidence is incomplete.** Corpus provenance exists, but
   it does not establish a supported compiler/runtime/dependency matrix for every
   example. Record exact tested baselines, compatible alternatives and limitations;
   separate browser/Node, CPython/embedded Python and platform-specific C assumptions.
8. **Framework material lacks project certification.** Python framework references
   need complete projects with pinned dependencies and meaningful unit/integration
   evidence. Spring's 12 seeds are plainly insufficient for complete readiness.
   Empty Rails/generic-web source folders do not establish a Rails/web course.
9. **Editorial grounding remains incomplete.** Imported material is labelled locally
   unverified. Every consequential explanation, complexity claim, do/don't and
   reference answer still needs source review and/or independent execution evidence.
   High record counts can conceal duplicates, inconsistent explanations and gaps.
10. **Retrieval/answer-safety assurance is limited.** The inventory has zero structural
    findings and scoped smoke probes, not a semantic relevance or adversarial proof.
    PDF/DOCX answer-boundary heuristics need editorial review; stale upload vectors
    remain excluded. More multi-source, weak-source, wrong-version, injection,
    conflicting-source and no-source evaluations are needed across all subjects.
11. **Teaching behavior is not certified across languages.** Live mentor checks were
    limited to JS/Java. Some replies give too much direction for their tier. Specific
    Java/JS factual guards withhold known overgeneralizations but are not general
    truth checkers. Reviews, hints, reflection, reveal and practice evidence need
    equivalent per-language verification and independent pedagogical review.
12. **Language transfer evidence is absent.** Explain equivalent ideas and important
    differences without claiming Java collections, JS arrays, Rust ownership or
    C pointers share identical semantics. Cross-language recall bonuses and learning-
    path sequencing remain deferred; no subscription behavior is changed here.

## Potential topic gaps requiring human/source review

These come from keyword scanning of answer-safe reference text, not an exhaustive
assessment of full payloads. A missing keyword is a review lead, not proof of
absence; a matching word does not establish mastery. The scan is not an adequate
framework-specific checklist, so Spring/framework subjects are omitted here.

- **c:** errors, modules-dependencies, dynamic-programming, greedy-backtracking
- **embedded-c:** errors, modules-dependencies, search-sort, linked-lists, dynamic-programming, greedy-backtracking
- **cpp:** No missing matches in the small scan; completeness still unestablished.
- **java:** No missing matches in the small scan; completeness still unestablished.
- **javascript:** No missing matches in the small scan; completeness still unestablished.
- **embedded-python:** recursion, search-sort, linked-lists, dynamic-programming, greedy-backtracking
- **python:** No missing matches in the small scan; completeness still unestablished.
- **ruby:** dynamic-programming
- **rust:** No missing matches in the small scan; completeness still unestablished.
- **typescript:** dynamic-programming

## Requested HTML/CSS and other absent catalog subjects

There are no dedicated HTML or CSS subjects in the packaged inventory. Small
snippets in framework documents cannot establish a complete HTML/CSS foundation.
There is no dedicated subject for the requested ReactJS, Angular, NextJS, Remix,
GatsbyJS, Astro or Solid practice, nor a dedicated Web Fundamentals/Web APIs course.
Their future scope remains deferred; accidental mentions in documents would not
count as those offerings. Existing design-pattern catalog entries number only
three (`shared-instance`, `shared-instance-javascript`, `strategy-pattern`), not a
verified patterns collection for every language.

HTML/CSS require browser-based semantics, layout, interaction and accessibility
checks; the existing function runner cannot validate those competencies. The
[prompt pack](training-prompts/README.md) specifies candidate output and independent
review, but does not implement a browser runner, importer or new practice subjects.

## Suggested language additions — recommendations, not commitments

My suggested priorities are SQL and Go, followed by C#; Kotlin, Swift and Bash
provide additional platform/tooling breadth. This is a product-fit judgement,
not a demand ranking. Stabilize existing subjects alongside any expansion.

| Addition | What it adds | Appropriate practice |
| --- | --- | --- |
| SQL, initially one explicit PostgreSQL dialect | Relational data and query reasoning useful across application stacks | Joins, grouping, NULL, windows, constraints, transactions and query plans; SQL workouts rather than forcing function-style DSA |
| Go | Another backend language and concurrency model | Fundamentals, slices/maps, interfaces, errors, goroutines/channels, testing, DSA |
| C# | .NET ecosystem and a different managed-language toolchain | Types/collections, generics, LINQ, async, testing and DSA |
| Kotlin | JVM language alternative and potential Android expansion | Nullability, collections, functional idioms, coroutines, tests and DSA |
| Swift | Apple-platform language and value/reference semantics | Optionals, enums/protocols, collections, concurrency, tests and DSA |
| Bash (optional specialist track) | Shell automation and process/file reasoning | Quoting, pipelines, exit status, safe fixtures and automation tasks; not a priority for conventional DSA |

Authoritative starting material: [PostgreSQL tutorial](https://www.postgresql.org/docs/17/tutorial.html),
[Go tutorials](https://go.dev/doc/tutorial/),
[C# tour](https://learn.microsoft.com/en-us/dotnet/csharp/tour-of-csharp/overview),
[Kotlin documentation](https://kotlinlang.org/docs/),
[Swift getting started](https://www.swift.org/getting-started/),
[GNU Bash manual](https://www.gnu.org/software/bash/manual/).
These subjects are not in the current packaged inventory; incidental code or source
folder mentions have not been certified as complete offerings. None was added here.

## Deferred plans recorded from the owner

After the present gap report and HTML/CSS prompts:

- Essential JavaScript and TypeScript, optional HTML and/or CSS practice, then a
  chosen UI library/framework: ReactJS, Angular, NextJS, Remix, GatsbyJS, Astro,
  Solid, and potentially others. Exact pathways/prerequisites are undecided.
- Web Fundamentals: owner will define the precise scope later.
- Framework-specific exercise banks: fundamentals, idioms, dos/don'ts, debugging,
  UI-related algorithms and relevant design patterns. Treat these as applied UI
  engineering workouts; classical DSA can be included where it genuinely applies.
- Web APIs: understanding and practical usage; scope to be planned later.
- Design patterns across all knowledge-base languages, with idiomatic alternatives,
  tradeoffs, counterexamples and practice rather than rote pattern-name recall.

Future planning should distinguish optional HTML/CSS workout participation from
HTML/CSS understanding needed by a selected UI task. That is an open dependency
question, not a decision made by this report. No deferred framework curriculum,
API course, pattern bank, pricing or subscription system was implemented here.

## What was done now

Refreshed the whole-library inventory; consolidated evidenced gaps and review
unknowns; supplied language recommendations and primary sources; wrote two complete
reusable generation prompts plus independent-review/batching instructions; recorded
later plans. No generated knowledge was approved or indexed and no paid model calls
were made. A prompt alone cannot guarantee perfect data or exhaustive coverage.

Verification for these deliverables: 12 audit/reference-library tests passed;
Markdown fences, local links, embedded JSON template/scalar metadata and whitespace
checks passed. No application behavior changed, so the full application suite was
not rerun for this documentation-only update.
