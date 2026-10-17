# JavaScript and Java release corpus

`java-javascript.jsonl` is the canonical packaged copy of the original
`Training Data/dsa_mentor_rag_export/dsa_curriculum.jsonl`: 4,280 records,
2,377 Java and 1,903 JavaScript. Do not ingest overlapping cumulative exports.
The original export is preserved outside the API project.

Each JSONL line contains `id`, `document`, scalar `metadata`, and `payload`.
`document` is retrieval text; `payload` retains original examples and answers.
The API never returns arbitrary payloads to learners. Preserve original
`verified` values: they are source claims, not evidence from this release.

The adapter in `app/services/curriculum.py` exposes 274 concept records as
supplemental lessons. Only explicitly answer-free records are eligible for
retrieval; exercises and gotchas are excluded. It adds the app's track,
problem ID, corpus version, and language metadata. Embedded programming,
frameworks, design patterns, and TypeScript are outside this release corpus.

The primary shared path is authored in `data/content/language/*-path-*.md`:
12 matching stages for each language, ordered by `order` and linked through
`prerequisites`. Each has a lesson, worked example, misconception, exercise,
starter signature, six hidden tests, and a protected reference solution.
Tests establish correctness on those inputs, not exhaustive mastery.

Run from the API directory:

```sh
.venv/bin/python tools/validate_curriculum.py
.venv/bin/python -m pytest tests/test_release_curriculum.py -q
```

Java verification needs a working JDK. Set `JAVA_HOME` in `.env` to its home
directory if it is not on PATH. The local workstation uses its existing
DataGrip bundled JDK; configure a standalone JDK on deployment machines.

The supplied validator reports zero errors for this canonical file.
Provenance URLs and source verification are incomplete; the larger source
corpus still needs editorial review. This release does not certify every
archived PDF, DOCX, or code snippet.
