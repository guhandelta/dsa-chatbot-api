# Typed assessments and debugging understanding checks

All quiz languages use the same assessment contract, grounded in each item's
language, question, snippet, private reference answer/solution and explanation.
MCQs retain their existing grading. Typed answers require two additional strings:
`reasoning` and `transfer` (nonempty, at most 4000 characters each).

The learner first writes an answer, then explains a specific step and supplies a
changed case with its expected result and justification. The server submits all
three together; keys remain private until the final submission. This is a
learner-proposed variation, not a generated question bank or an authorship test.

An understanding rubric scores reasoning and transfer separately. Both must
reach 0.6 and the original answer must pass for the item to count as correct.
The item score averages the original score and the understanding score; an item
that fails either requirement is capped at 0.599. Code's original score uses the
fraction of hidden tests passed. These checks do not replace hidden tests.
Historical scores are unchanged.

`POST /study/debug/challenges/{attempt_id}/assess` accepts `diagnosis`, `reasoning`
and `transfer`. The latter must explain a concrete regression test. The rubric
uses the challenge's private solution. A failed check retains the assigned
challenge for revision. A passing check marks it reviewed, without awarding
pathway mastery or claiming executable verification. The old `/review` endpoint
remains a self-review compatibility path and awards no mastery. Debugging
review counts therefore include legacy self-reviews and rubric-reviewed work.

Provider failure, timeout, ambiguous reference or invalid model output yields
503, without awarding credit or returning an answer key. The UI retains drafts.
Debug checks reserve an attempt and enforce a one-minute retry cooldown; stale model
responses cannot mark skipped/replaced attempts reviewed. Model-based feedback
can still be mistaken; these are formative checks, not certified high-stakes
assessments. No style-based AI detector, paste blocking or surveillance is used.
Grader-call reservations, including failures, share an hourly usage limit across
typed quizzes and debugging checks. They contain no student answer text.

## Rollout

1. Back up the application database.
2. Run `.venv/bin/alembic upgrade head` from the API directory (migration
   `0021_understanding_checks` adds nullable evidence columns and a usage-reservation
   table, preserving old rows).
3. Deploy/restart API and UI together. Older UI versions cannot submit typed
   quiz answers without the newly required reasoning fields; refresh open tabs.
4. Configure an existing supported LLM provider for rubric grading. Without one,
   typed submissions stay unsubmitted, and the learner can retain their draft.

Checks are shared across every bank language and every debug subject, including
framework investigations. This does not add missing execution runtimes.

Automated tests exercise the contract with deterministic model doubles, including
invalid/nonfinite grades, missing fields, provider outages, replay, ownership,
partial credit, per-language coverage, and saved drafts. They do not certify the
semantic accuracy of a live model across the full bank.
