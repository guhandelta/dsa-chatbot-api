# Debugging knowledge base

`knowledge-base.json` is the dedicated runtime bank. It currently preserves 2,454
code investigations from the existing authored sources. These are self-review
activities, not 1,982 independently executed or graded tests. Some are trace
questions with correct code; `task_kind` distinguishes those from repairs.

The API returns only its explicit public field list. `solution`, `node_ids` and
`source_ids` stay server-side. Do not copy this file into public UI assets.

## Adding problems supplied by the author

Author input lives in `data/curriculum/debug-challenges.json`. A case needs:

| Field | Meaning |
|---|---|
| `language` | Subscription language, e.g. `java` |
| `subject` | Exact existing subject, e.g. `spring-boot`, owned by that language |
| `difficulty` | `easy`, `medium`, `hard`, `expert`, or `extreme` |
| `title`, `code` | A distinct scenario and its investigated snippet |
| `failure` | Actual failing behavior or answer-free investigation question |
| `goal` | What the learner should diagnose and which regression test to propose |
| `private_solution` | Editorial diagnosis/corrected example; never public |
| `node_ids` | Exact path topics; required for core topic placement |
| `code_language` | Syntax used by the snippet; defaults to subscription language |
| `task_kind` | `repair` or `trace`; defaults to repair |
| `explain_unit_ids` | Optional exact tiered Explain IDs, e.g. `explain:javascript:arrays-strings`; combined topics require their own matching cases |

For generated source scenarios, edit `tools/build_debug_challenges.py`; running
that builder overwrites the authored input JSON. To add cases directly to the
input JSON, skip the builder when publishing those edits.

Publish deliberately, then audit:

```sh
.venv/bin/python tools/compile_debug_knowledge.py
.venv/bin/python tools/audit_debug_challenges.py
.venv/bin/pytest -q tests/test_debug_challenges.py tests/test_study_progress.py
```

The compiler also explicitly imports eligible local reference/quiz snippets. The
live API does not read those sources to construct its bank. Preserve provenance;
reference imports are starter reasoning material, not proof of executable validity.

Identifiers derive from language, subject and whitespace-normalized code. Keep
unchanged identifiers stable to preserve no-repeat history. Changed code creates
a new identity; editorial review must catch superficial variants of the same bug.
Retired IDs remain in student history but do not inflate current-bank charts.

Missing topic/difficulty content displays Coming soon. Exhaustion displays a
separate message and never silently substitutes another topic or restarts history.
The current audit verifies language markers, topic ownership, coverage, fingerprints
and private-answer boundaries. It does not establish semantic correctness or difficulty.

## Before enabling automatic grading

Add versioned runtime/framework dependencies, setup fixtures, failing tests,
expected behavior, a working correction and regression tests. Confirm the original
fails for the intended reason and the correction passes. Use an isolated runner
with no application secrets or host mounts, bounded resources and network access.
For framework scenarios, specify the surrounding project/configuration needed to
reproduce the issue; a short snippet alone often cannot establish the failure.

Keep generated drafts outside this published bank until validated and reviewed.
An LLM approving another LLM's diagnosis does not replace execution evidence.
