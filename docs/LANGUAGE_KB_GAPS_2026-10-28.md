# Language knowledge and executable-coverage gaps

Audit refreshed: 2026-10-28. The inventory reads the packaged corpus and the
local published-upload database. It does not infer quality from a `Published`
badge: published means retrieval-eligible after curation, not fact-checked,
executed, or pedagogically certified.

## Current evidence

- Packaged knowledge audit: **19,973 records, 12 language/subject labels, 28
  subjects, zero structural findings**. It checks metadata and retrieval probes;
  all records remain `not_certified` because it does not execute lessons or
  establish factual/pedagogical completeness.
- Language-integrity audit: **180 path nodes, 2,097 quiz items, 81 course
  sources, 157 module sources, and 899 authored code blocks**, with zero static
  integrity errors. This is a schema/source check, not a correctness proof.
- Published uploads: **239**. The refreshed answer-safe projection audit has
  **zero failures**. Three course-plan documents are now excluded from learner
  retrieval. The remaining 236 are mechanically available to retrieval.
- Of those learner-eligible uploads, **131 have an empty stored language field**.
  Validated front matter or filename evidence now scopes 127 of them to a
  specific language. Four Swift/Kotlin Blind 150 files have no single-language
  scope; their shared, answer-safe problem-reference text remains
  `all_languages`. No database rows were rewritten and no re-embedding was
  performed. The retrieval projection resolves scope at query time.
- The live-upload audit proves safe projection and sample retrieval, not that
  every source paragraph survives curation or that every factual claim is true.
  Review status and execution evidence remain separate.

## Language-by-language completion state

| Group | Languages | Present evidence | Remaining language work |
| --- | --- | --- | --- |
| Audited executable benchmark | Python, JavaScript, TypeScript, Java, C, C++, Rust, Ruby, Go, C# | The saved exercise audit records 49 passing references and 399 fixture checks per language (3,990 total). | Re-run in the configured Docker image when available; expand independent oracle/fuzz coverage and review explanations. Existing audit evidence is finite, not proof over all inputs. |
| New function-grader languages | PHP, Dart, Kotlin, Swift, Scala, Haskell | Function-test adapters exist. Substantial language-specific course, quiz/debug, and DSA sources have been uploaded and are retrieval-eligible under their scopes. | The app has no authored 12-stage language pathway or quiz-bank JSON for these six, and the 37 shared DSA problem files have no discoverable reference sections for them. To match the 49-item benchmark, author 12 runnable foundation exercises plus 37 DSA references/fixture sets for each: **72 foundation sets and 222 DSA references**. Then audit each language. |
| Web fundamentals | HTML, CSS (plus Sass, Bootstrap, Tailwind, Bulma, shadcn subjects) | Packaged and uploaded conceptual material exists. | These are not function-grader languages. Add browser/project checks and accessibility review before claiming executable UI coverage. Frameworks remain a separate project-verification task. |
| Embedded subjects | Embedded C, embedded Python | Concept and debugging material exists; additional candidate references are generated in the sibling gap-fill package. | Name the target board/toolchain for hardware claims. Host-side algorithm tests do not certify peripheral behavior, timing, memory use, or circuit simulation. |

### Confirmed app integration gaps for PHP, Dart, Kotlin, Swift, Scala, Haskell

The uploaded files already contain broad learning content. A second general
prose corpus would duplicate it. The current application integration gap is
visible in the source:

- `app/services/learning_path.py` includes only ten languages in
  `LANGUAGE_LABELS`; these six do not appear as language learning paths or
  Study Room quiz choices.
- `data/curriculum/quiz/` contains banks for those same ten languages, not the
  six newly supported languages.
- `data/content/language/` contains no authored stage lesson/exercise files for
  those six.
- The canonical 37 DSA files include references for the ten audited languages,
  but not these six. Uploaded DSA catalog documents do not substitute for
  discoverable code references plus app fixtures.

This is why publishing and retrieving their large language corpora does not
make their executable curriculum complete.

## Remaining content and review work

1. **New languages: generate app-ready exercises, not duplicate manuals.** For
   each of PHP, Dart, Kotlin, Swift, Scala, and Haskell, produce 12
   language-specific foundation tasks aligned to the shared path, each with a
   contract, starter signature, fixtures, expected results, and a hidden-edge
   case. Add language implementations and fixtures for all 37 canonical DSA
   problems. Keep Haskell and Scala assessment focus appropriate to functional
   programming/data engineering; do not force interview questions where they
   do not teach the language.
2. **Run the function-reference audit per language.** A task counts only after
   its reference is discoverable through the real content catalog, fixtures
   pass in the pinned runtime, and known-bad implementations are rejected.
   Current tool execution could not reach Docker (`permission denied` on the
   local Docker socket), so the 49/399 benchmark for the original ten is based
   on the saved dated audit, not a fresh container run today.
3. **Review versioned factual claims.** Uploaded language books identify target
   language versions and cite source material, but remain generated and
   unexpert-certified. Verify version-sensitive examples, Unicode/numeric
   behavior, runtime/library claims, complexity statements, and security advice.
4. **Resolve topic-scan leads in the packaged inventory.** The keyword audit
   still flags C greedy/backtracking; embedded C errors, search/sort, linked
   structures, dynamic programming and greedy/backtracking; C# and Go
   greedy/backtracking; embedded Python search/sort, linked structures,
   dynamic programming and greedy/backtracking; Ruby dynamic programming; and
   TypeScript dynamic programming. A missing keyword is not proof of missing
   knowledge. New candidate notes cover these leads in
   `Training Data/generated-gap-fill/remaining-language-scan-leads-v1/`; they
   must be independently reviewed and uploaded before they count as app data.
5. **Frameworks follow language readiness.** Spring, Django, Flask, FastAPI,
   Laravel, Rails, Flutter, Android, iOS, and Spark need pinned project
   templates with build/unit/integration checks. Knowledge-base prose alone
   cannot verify framework execution.

## Changes made during this refresh

- Upload retrieval now honors a validated `language:` field in Markdown front
  matter when legacy database metadata is blank, after explicit upload metadata
  and before filename fallback. Conflicting explicit/front-matter scopes are
  withheld instead of relabelled.
- Filename inference now recognizes PHP, Dart, Kotlin, Swift, Scala, and
  Haskell.
- The three web curriculum/planning PDFs are excluded from learner knowledge
  retrieval.
- The uploaded-library audit reports the effective projected scope and applies
  subject-scoped retrieval probes to avoid false failures caused by unrelated
  high-frequency lexical matches.
- Seven supplementary candidate references were generated for the remaining
  packaged topic-scan leads. They are explicitly unverified and are not yet
  indexed by the app.

## Verification

- `tests/test_uploaded_knowledge.py`: **31 passed**.
- `tools/audit_uploaded_knowledge.py`: **239 published, 236 eligible, three
  planning documents excluded, zero projection/retrieval failures**.
- Full packaged audits: knowledge structural audit passed (19,973 records),
  language-integrity audit passed (180 path nodes; 2,097 quiz items), and
  assessment-bank audit passed (1,445 items). These are static audits.
- Docker-dependent execution was not rerun because this environment cannot
  access the Docker Desktop socket. No new code/reference solution is described
  as execution-verified.
