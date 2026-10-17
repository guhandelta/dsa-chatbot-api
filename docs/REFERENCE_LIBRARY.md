# Additional training data and reference learning

The additional corpus is now part of the application's local RAG knowledge
library. This is reference ingestion, not model fine-tuning or certification of
new executable courses. JavaScript and Java fundamentals remain in their
existing canonical corpus and verified exercise paths.

## Current import

The import retains **13524 records**, of which **9700 reference views** are
eligible for learner retrieval. It examines JSONL exports, ZIP members, DOCX
blueprints, and PDFs under the existing `Training Data` directory. The current
manifest records 801 source/member entries, zero parsing errors, and zero
conflicting IDs. C material comes from cumulative exports even though the
standalone C folder is empty. The Ruby-on-Rails and generic web folders are
empty; no Rails-specific course was invented.

| Subject | Retained records |
| --- | ---: |
| C | 1369 |
| C++ | 414 |
| Embedded C | 2094 |
| Embedded Python | 1102 |
| Python | 397 |
| Python Django | 708 |
| Python FastAPI | 708 |
| Python Flask | 708 |
| Ruby | 1179 |
| Rust | 3218 |
| TypeScript | 1615 |
| Spring starter references across six subjects | 12 |

These counts include withheld exercise/gotcha candidates and source material;
they are not counts of verified workouts. Blueprint chunks and structured
records can discuss overlapping topics. Byte-identical copies and repeated IDs
are deduplicated. Different records with conflicting content under one ID would
be quarantined, rather than silently selecting one. Python Unicode line
separators inside JSON strings are preserved correctly.

## How to use it

Open **Chat**, then choose a subject from **Reference library**. The interface
selects the subject's language and starts a separate chat scope. Spring MVC,
Spring Boot, Python frameworks, and embedded topics require explicit subject
selection, so they do not silently enter unrelated language or DSA discussions.
This does not change language preferences, mentor entitlements, prices, or the
list of verified workout languages.

The API exposes `GET /tracks/reference-subjects` for authenticated inventory.
Example authenticated chat body:

```json
{
  "message": "Explain the DispatcherServlet request flow",
  "language": "java",
  "track": "language",
  "subject": "spring-mvc"
}
```

Unknown subjects, a mismatched language/track, or combining a reference subject
with a focused lesson are rejected before a charge. Ordinary chat usage pricing
still applies. Source claims of verification are preserved in raw payloads but
the imported metadata explicitly says **not locally executed**. Hardware/runtime
context is retained when supplied. New reference IDs cannot be submitted as
verified workouts through the practice endpoints.

## Answer safety and limitations

Exercise and gotcha records, including alternate/plural source kind names,
remain outside learner retrieval. DOCX and PDF reference views stop at detected
exercise, answer-key, or solution headings. Full extracted source text is kept
in the private payload where applicable; only the reference view is retrieved.
Editorial review of the supplied blueprints remains necessary: heuristic
section boundaries are not a formal guarantee about arbitrary source content.

The RAG service rechecks subject, language, kind, and answer flags on selected
reference results, including vector results. Imported snippets, expected
answers, hardware examples, and framework projects have not been executed by
this ingestion. Existing verified JavaScript/Java admission checks remain in
place and have not been extended to these candidates.

## Spring collection

Twelve original short reading cards were gathered from official documentation:
Spring IoC; MVC and DispatcherServlet; annotated controllers; Boot overview,
auto-configuration and external configuration; MockMvc and Boot testing;
transactions; Servlet security; and Spring Data JPA.

The cards retain their official source URLs and observation date. Sources
include [Spring MVC](https://docs.spring.io/spring-framework/reference/web/webmvc.html)
and [Spring Boot](https://docs.spring.io/spring-boot/reference/index.html).
They are a starter reference set, not a complete Spring curriculum. Next steps
are selecting a Java/Boot/Framework version baseline, collecting deeper
version-specific lessons, adding independently checked examples and projects,
and executing controller, validation, persistence, security, and integration
tests before enabling framework workouts.

## Repeat the import

From the API directory:

```sh
.venv/bin/python -m tools.import_reference_library
```

The importer does not execute training-directory scripts or extract archive
paths onto the filesystem. Source/member hashes and provenance are recorded in
`data/reference_library/manifest.json` and `records.jsonl`. Reimports replace the
records and manifest atomically per file; runtime records and BM25 caches detect
source replacement. The source archives remain unchanged.

No paid LLM or embedding calls were made during this import. The new knowledge
is available through local BM25 retrieval in the existing RAG flow. Existing
Chroma/PGVector collections were not rebuilt. The normal knowledge-base refresh
now includes eligible supplemental records if a real embedding refresh is
chosen later; that operation can incur provider costs. The application still
needs a model provider to generate chat answers.

## Verification for this import

- 358 backend tests and 61 frontend tests passed.
- TypeScript checking, the frontend build, and migration drift checks passed.
- Retrieval smoke checks passed for all 17 imported subjects.
- A complete repeated import produced identical `records.jsonl` bytes.
- Tests cover duplicate/conflicting IDs, Unicode separators, answer exclusion,
  subject/language isolation, selected-subject vector filtering, pre-charge
  request validation, UI subject propagation, and cache refresh after reimport.

Live-provider answer quality, hardware execution, and framework-project tests
remain outside this ingestion's verification scope.


## Approved `/learn` PDFs (October 15 follow-up)

Approved uploads now have a separate database-authorized local retrieval path.
Legacy upload vectors remain excluded; answer/code sections are withheld in
conservative projections. New uploads carry an explicit language, and rejected,
deleted or replaced sources cannot reach chat through stale vectors. See
[reliability verification](RELIABILITY_VERIFICATION.md) for boundaries and audits.
