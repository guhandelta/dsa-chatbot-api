# Verification status and content admission

This is a private application under construction. Passing an executable suite
is evidence for the supplied cases, not proof that a curriculum is complete or
that every possible input is correct.

## Implemented admission rules

- JavaScript/Java practice starts, submissions, and solution reveals require a
  passing reference execution before they can proceed. A failing reference,
  missing runtime, absent solution, malformed fixtures, or fewer than six
  distinct fixture inputs blocks admission. Preflight failures do not charge
  usage credits or create learner progress.
- Reference checks are cached against source bytes, path, language, and runtime
  availability, execution backend, and container image. Content edits invalidate the check; an old audit file does not
  authorize new content. Checks read fixtures and reference code from the same
  source snapshot. Restart the service after replacing an installed runtime.
- Function outputs preserve array and matrix ordering by default. Boolean and
  numeric results are distinct. Two Sum explicitly allows index reordering;
  3Sum explicitly allows triplet and result ordering changes. Multiplicity is
  preserved. Authored problems must declare their comparison contract.
- Linked-list exercises serialize fixture arrays into actual nodes and serialize
  returned nodes back into arrays. Cycle/excess-output checks reject invalid
  results. Current node adapters support JavaScript, Java, and Python.
- Java unsigned 32-bit exercises use `long` for values up to 4294967295; their
  statements and references use the same numeric contract. Java word-list
  parameters can receive `List<String>` through the typed execution adapter.
- Instructor DSA publishing requires JavaScript and Java references, unique
  solution languages, finite JSON fixtures with at least six distinct inputs,
  and complete passing execution of **every supplied implementation**. Missing
  toolchains and compilation-only checks block publishing. The six-language LLM
  generator may therefore produce a draft requiring review on this machine.
- Fixture data, entry points, and output-comparison rules survive publication.
  An indexing failure does not put a new exercise file in the learner catalog;
  successful source publication uses atomic file replacement. The filesystem
  and vector database do not share a distributed transaction.

## Repeatable audit

From the API directory:

```sh
.venv/bin/python -m tools.audit_exercises --output docs/exercise-audit.json
.venv/bin/python -m tools.validate_curriculum
```

The first command executes current DSA and language exercises in JavaScript and
Java. Exit status 1 means at least one reference is blocked. Its JSON report
records source hashes, per-language execution, case counts, and limitations.
The second checks the packaged JSONL corpus structure and internal links; it
does **not** execute or establish correctness of its educational answers.

## Remaining curriculum work

The current executable scope is 23 DSA problems in each of JavaScript and Java,
plus 12 foundation lessons per language: 70 language-specific reference checks.
Reference-only concept pages and the packaged corpus exercises are not promoted
to verified workouts by this audit. Full switching pathways, advanced workouts,
TypeScript, broader editorial validation,
and live mentor-quality evaluation remain incomplete. The current 23 DSA fixture
sets now also pass independent small-input mathematical/exhaustive oracles. Other language versions
need their own execution audit and adapters before claiming equal coverage.

## Hint cycles and retained credits

The default cycle is 1008 hours (42 days). It is anchored to the first hint for
each learner/problem/language and repeats at fixed boundaries. Recent requests,
new practice sessions, and subscription renewals do not postpone the reset.
Learners retain their reflections and learning history when the hint tier resets.

Subscription expiry and cancellation never modify a peppercorn balance.
Remaining credits can fund chat and reviews without renewing. Mentor questions
still require a valid language entitlement under the current access rules;
commercial pricing and which future features require payment remain undecided.

Mentor recall searches earlier reasoning with overlapping technique tags, including
hint notes and reflections. The owner provisionally allows both verified-solve
material and unfinished hint reasoning, to revisit later. Prior attempts are not
described as proven successes. Cross-language recall is proposed as a tentative multiple-language subscription
bonus; allowances and enforcement remain undecided. Current hint and review
recall is restricted to the selected language; future cross-language bonuses are disabled. See [product decisions and
subscription packaging notes](PRODUCT_DECISIONS.md).
