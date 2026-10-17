# Remaining verification — October 15, 2026

## Outcome

The replacement OpenAI key works with the application evaluation harness. The
owner approved sending approved reference excerpts for the full comparison,
which completed all twelve responses. The earlier automatic-review rejection
was resolved by that explicit approval; no credential is included in reports.

Retain standard RAG as the default and the agentic pilot as disabled/admin-only.
The experiment is operational within its tested boundaries, but does not justify
converting the entire application or claiming perfect teaching/security.

## Live OpenAI comparison

Six fixed JavaScript/Java questions, ten expected PDF references, the configured
`gpt-4o-mini` model, zero SDK retries, up to two read-only searches and three
model calls per agentic response. The local baseline used the same stores and
one answer call. Request order alternated. No embedding calls were made.

| Measurement | Local one-shot baseline | Agentic |
| --- | ---: | ---: |
| Completed responses | 6/6 | 6/6 |
| Expected PDFs in answer context | 7/10 | 8/10 |
| Expected PDFs cited | 7/10 | 8/10 |
| Median latency | 1.655 seconds | 3.744 seconds |
| Model calls | 6 | 18 |
| Reported input tokens | 5,691 | 14,658 |
| Reported output tokens | 717 | 1,008 |

This run used approximately 2.44 times as many total tokens for agentic retrieval.
That is not a monetary cost ratio or an accuracy score. Agentic retrieval did not
find every expected PDF; the Java stacks/queues and JavaScript arrays/linked-list
comparisons each missed one target. An equivalent concept source can still be
useful without matching the exact expected filename.

The six-question artifact is a **pre-qualification-guard** snapshot. The earlier
Gemini comparison also predates that guard (context coverage 7/10 versus 9/10,
median latency 2.769 versus 6.413 seconds). The two providers were run at different
times, so these numbers do not establish a provider ranking. Neither baseline
represents the complete production vector-retrieval pipeline.

Evidence: [OpenAI six-case responses](agentic-rag-openai-evaluation.json),
[original Gemini comparison](agentic-rag-evaluation.json).

## Defects exposed and fixed

1. **Container paths:** compiled executables could lose their `/work` path;
   macOS temporary-directory aliases could also escape translation. Scratch
   paths now resolve before translation, including the executable itself.
   Regression tests cover compiled paths and symlink aliases. External tool
   paths such as a host JAVA_HOME resolve to the tool name inside the image.
2. **Pinned local images:** an immutable local `sha256` image ID is now accepted
   alongside repository digests. Mutable image tags remain rejected at runtime;
   Docker pulls are disabled during student execution.
3. **Mentor question contract:** a real reply contained two questions. Outputs
   outside the one-question/length contract now use a deterministic tier fallback
   without another provider call. Tier 4 prefers a tagged technique over a broad
   data-structure category. Existing code-output withholding still applies.
4. **Known teaching overgeneralizations:** live replies generalized Java hashing
   to every Map/Set and JavaScript arrays to guaranteed contiguous storage.
   Adding trusted prompt qualifications alone did **not** fix this reliably.
   A conservative output guard now withholds those detected claims and asks for
   the collection implementation or relevant operation/engine instead. It clears
   source citations so the trusted replacement is not falsely attributed to PDFs.
   This guard applies to both ordinary chat and the experiment.

The qualification follow-up reran both strategies on the two affected questions:
**4/4 completed**, all four unsafe generated claims withheld. These were safe
clarifications, **not four successful substantive answers**. The full six-case
comparison has not been rerun after that guard; do not apply the earlier coverage
and latency figures to the latest implementation without this qualification.

Evidence: [prompt-only failure snapshot](teaching-qualification-openai-before-guard.json),
[guarded follow-up](teaching-qualification-openai-evaluation.json).
Executable Java tests demonstrate different HashSet/TreeSet equivalence; JavaScript
tests exercise sparse arrays and object properties. These tests validate their
examples, not every model claim or every engine's internal memory representation.
Technical references: [Oracle TreeMap contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/TreeMap.html),
[ECMAScript array exotic objects](https://tc39.es/ecma262/2024/multipage/ordinary-and-exotic-objects-behaviours.html#sec-array-exotic-objects).

## Live mentor verification

Eight bounded calls per provider cover all four tiers in JavaScript and Java:
**OpenAI 8/8 and Gemini 8/8** returned one question without fenced code after the
question guard. Calls used a synthetic Two Sum learner and explicitly labelled
unfinished recall; maximum 350 output tokens/call and zero SDK retries. No reply
labelled the unfinished reasoning as a verified solve.

Review still found pedagogical weaknesses: an OpenAI tier-1 reply suggested
keeping track of seen numbers prematurely; some tier-4 replies described storing
values while iterating rather than merely naming the family. A generic fallback
about the smallest valid input is less useful for a performance complaint.
Question counts and code screening do not certify tier fidelity. An independent
human pedagogical review remains pending. These are documented limitations,
not resolved by making replies end in one question.

Evidence: [OpenAI replies](mentor-openai-live-evaluation.json),
[Gemini replies](mentor-gemini-live-evaluation.json),
[original two-question failure](mentor-openai-before-question-guard.json).

## Real Docker verification

Docker Desktop was started and a local verification image built; nothing was
published to a registry. The Dockerfile pins the base resolved during that build.
Runtime audit identity:

`sha256:f5c5615782bc58561f3e1e5c92576703a1b0f1772391ca3e8c6d2b0bdd8ad1b0`

All **11 isolation checks passed**: host marker hidden, network denied, root
read-only, host environment sentinel absent, capabilities dropped/no new
privileges, enforced memory and process limits, output capped at 65,536 bytes,
infinite loop timed out, six-language execution, and no new running containers
left behind. Resource limits checked 512 MiB memory and 64 processes. Six small
cases each passed in Python, JavaScript, C, C++, Java and Rust (36 checks).

All **70 JavaScript/Java curriculum/reference implementations passed 422 fixture
checks in this image**, with zero blocked references. Go and TypeScript were not
included in this image's runtime certification. Broad Python/C/C++/Rust problem
coverage is not established by their six-case smoke tests. The three Java
precision tests also passed inside Docker: seeded differential fuzzing accepted
the reference and detected a deliberately broken implementation, growing-size
in-process timing ran, and invalid workload ordering was rejected. Timing remains
noisy evidence rather than a complexity proof.

Evidence: [isolation report](container-isolation-evaluation.json),
[full JS/Java container audit](container-exercise-audit.json),
[Dockerfile](../sandbox/Dockerfile).

Operator reproduction (from the API repository):

```sh
docker build --tag dsa-verification:20261015 --file sandbox/Dockerfile sandbox
docker image inspect dsa-verification:20261015 --format '{{.Id}}'
EXEC_BACKEND=docker EXEC_CONTAINER_IMAGE=sha256:f5c5615782bc58561f3e1e5c92576703a1b0f1772391ca3e8c6d2b0bdd8ad1b0 .venv/bin/python tools/check_container_isolation.py
```

A rebuild can install newer packages and produce a different image ID; inspect
and audit that new immutable ID before using it. This verifies the tested local
image and Docker configuration, not a kernel/container escape proof or production
load certification. The app's `.env` was not changed: its current backend remains
`subprocess` for trusted private development, which does not isolate host files
or networking. The agentic flag also remains false. Docker Desktop and the local
verification image remain available on this machine.

## Regression and data integrity

- Backend final suite: **486 passed**, one LangGraph dependency deprecation warning.
- UI: **69 passed**; TypeScript and production build passed.
- Java precision inside Docker: **3 passed**.
- Python compilation, curriculum structural validation, and Git whitespace
  checks passed. The current curriculum passes structural validation; this does
  not certify all imported teaching claims or complete its deferred design.

All **38/38** approved PDF retrieval probes passed, including wrong-language
exclusion. Original text hashes and approval fingerprints match the prior audit.
SQLite integrity is **ok**, **zero ledger mismatches**, and all 38 documents remain
published. Migration/model column checks passed. No approval records, embeddings,
learner progress, balances, subscriptions or payment policies were changed by
these operator comparisons. Provider calls consumed real account usage and do
not debit learner peppercorns.

## Remaining work and limits

- Improve tier fidelity and question usefulness; run independent learner and
  editorial reviews. Neither provider is guaranteed to obey every semantic rule.
- The teaching guard recognizes specific known patterns; it can miss differently
  worded errors and can conservatively withhold valid answers. Citations alone
  cannot prove grounding, correctness or absence of solution leakage.
- Expand the six-question evaluation with adversarial and weak-source examples,
  larger corpora, concurrency/load measurements and a stronger deterministic
  retrieval baseline. The upload candidate window remains limited to 100 recent
  potentially matching approved documents in the experiment.
- Live Claude behavior, all supported language runtimes, every provider failure
  mode and production-scale operational resilience remain unverified.
- The existing 333 reference-only items and 67 packaged non-executable exercises
  are not certified workouts. Fixtures and fuzzing support confidence within
  tested domains; they are not formal proofs of all valid inputs or complexity.
- A running API process needs restart to load the replacement key and code.
  This work ran isolated verification commands; it did not deploy/restart the API
  or enable experimental features.
- Curriculum/pathway structuring, subscriptions, pricing/payment packaging and
  proposed cross-language recall bonuses remain deferred as requested.
