# Agentic retrieval pilot — October 15, 2026

Follow-up: [OpenAI comparison, actual Docker execution and teaching guards](REMAINING_CHECKS_2026-10-15.md). The comparison below is a historical Gemini snapshot.

## Decision

Keep ordinary RAG as the default. The private agentic pilot works through its
bounded retrieval and response path, but the evidence does **not** establish
perfect answers or justify converting the whole application.

The final live Gemini comparison completed all 12 responses across six questions.
Agentic retrieval included more of the expected PDF references on two compound
questions, at greater latency and token usage. An overgeneralized Java equality
explanation remains a teaching-quality concern. An independent human pedagogy
review is still pending.

## Final live comparison

Both strategies used the same configured Gemini model, zero reasoning budget,
zero SDK retries, answer instructions, source protections and output validation.
The baseline made one original-query search against each local store and one
answer call. The agent chose up to two searches and made up to two planning calls
plus one answer call. Request order alternated between cases.

| Measurement | One-shot local baseline | Agentic retrieval |
| --- | ---: | ---: |
| Completed responses | 6/6 | 6/6 |
| Expected PDF references supplied in answer context | 7/10 | 9/10 |
| Expected PDF references cited | 7/10 | 9/10 |
| Median end-to-end latency | 2.77 seconds | 6.41 seconds |
| Model invocation attempts | 6 | 18 |
| Reported input tokens | 5,978 | 17,012 |
| Reported output tokens | 883 | 982 |

The agent used approximately 2.6 times as many total tokens in this run. That is
not a monetary price ratio: input/output token rates and provider billing differ.
These totals describe the final run, not every earlier debugging probe.

Coverage counts ten expected PDF references across six questions. The JSON
summary additionally reports per-question mean coverage; those percentages have
a different denominator. Source identity/coverage is **not answer accuracy**.
Equivalent information in a packaged concept record may be useful even when its
source name does not match the expected PDF filename.

This is a controlled retrieval comparison against a local baseline, **not** a
full production-vector-RAG benchmark. Ordinary application RAG still uses its
existing prompt/provider settings and vector fallback. The pilot deliberately
avoids embedding calls and stale upload vectors. Source balancing/reranking may
achieve some of the observed improvement without an agent; that stronger baseline
has not been benchmarked here. Six questions do not establish statistical
significance, p95 latency, broad language coverage or learning outcomes.

Artifacts:

- [Final live responses, citations and configuration](agentic-rag-evaluation.json)
- [Summary and review findings](agentic-rag-summary.json)
- [Question set](../data/evaluations/agentic_rag.json)
- Earlier failure evidence: `agentic-rag-gemini-initial.json`,
  `agentic-rag-before-thinking-budget.json`,
  `agentic-rag-before-citation-fix.json`. The OpenAI evaluation now records the successful follow-up.

The final report records the configured model and engine source SHA-256 so its
behavior can be distinguished from subsequent code edits. Intermediate reports
are historical debugging snapshots and must not be presented as the final run.

## Implemented boundaries

- `AGENTIC_RAG_ENABLED` defaults to **false**. The HTTP pilot additionally
  requires an authenticated **admin** and explicit `retrieval_mode: "agentic"`.
  Ordinary chat remains the default, including when the capability lookup fails.
- `GET /chat/capabilities` controls the private chat-screen opt-in. Switching
  modes creates a fresh UI conversation scope. The UI displays experiment
  duration/search/model-call counts and selected reference excerpts.
- Tools are limited to local curriculum search and approved upload search.
  There are no execution, network browsing, filesystem, payment, entitlement,
  progress-writing, solution-reveal or learner-memory tools.
- Language, track, subject and lesson are captured by server code. Extra model
  arguments and unknown tools are rejected. Returned documents are checked
  again for scope and explicit answer-safe metadata. Upload vectors cannot
  bypass SQL publication authority.
- Upload access is rechecked against current approval and source revision before
  answer dispatch and after generation. Rejected, deleted or changed sources
  cannot be returned through cached old excerpts. Content already sent to a
  provider cannot be recalled if its approval changes during that call.
- Two searches and three model calls maximum; no recursive agent execution.
  Planner output is capped at 300 tokens per call, answer output at 900.
  Input is capped at 16,000 UTF-8 bytes per call, selected source context at
  6,000 bytes/four excerpts, and experimental questions at 6,000 bytes.
- Each model call has a 10-second deadline; the request has a 30-second async
  deadline. Gemini's bounded factory sets `thinking_budget=0`. Other providers
  have separate bounded constructors and zero SDK retries.
- The upload tool considers at most 100 recent, potentially matching published
  documents; old unlabelled-language files also compete for this window. This
  limit can reduce recall as the library grows. Projection/ranking runs in a
  worker thread so it does not block the API event loop. A timed-out Python
  worker may finish its bounded local work afterward; it has no write tools.
- Context interleaves the two searches so the first batch cannot monopolize the
  entire source budget. Duplicate searches stop without another tool call.
- Malformed plans fall back once to a scoped original-query curriculum search
  within the same search/call ceilings. Empty results produce a clarification.
  Invalid final JSON, unknown citation IDs or revoked sources fail closed.
  Duplicate valid citation IDs are normalized; only supplied IDs are accepted.
- Obvious code-like answers and external URL/image output are withheld. The
  shared chat renderer suppresses embedded Markdown images as an additional
  browser boundary. Uploaded excerpts are rendered as escaped text.
- SDK usage is recorded when supplied. Failed calls mark usage incomplete rather
  than claiming known-zero usage. Counts indicate application invocation
  attempts; provider billing remains authoritative.

## Request integrity and concurrency

The pilot runs inside the existing keyed chat operation boundary. Replaying a
successful request returns the same receipt without another model call or debit.
Changing retrieval mode with an already-used key returns 409. Invalid output,
provider failures and timeouts roll back chat messages and refund a committed
reservation once. Disallowed pilot access, foreign thread IDs and oversized
questions are rejected before charging.

Chat now reads its bounded history and waits for generation **before** writing a
new thread. This avoids holding SQLite's writer lock throughout a long provider
call. A file-backed SQLite regression test starts a waiting chat and successfully
registers another learner while it waits. This does not claim unrestricted
parallel writes or production PostgreSQL load certification.

No subscription structure, pricing, credit amounts, curriculum pathways or
commercial feature policies were changed. The existing chat operation cost is
used in the private HTTP pilot; it is not multiplied per internal search/model
call. Operator CLI comparisons bypass learner credits while consuming real
provider usage.

## Findings from real execution and remaining limits

1. **Provider format mismatch:** Gemini returned fenced JSON. Parsing now accepts
   a single complete JSON fence while rejecting surrounding prose and unknown
   schema fields. Mock-only tests had not exposed this behavior.
2. **Reasoning/output budget conflict:** default Gemini reasoning consumed output
   allowance and left truncated JSON. The bounded factory now sets an explicit
   zero reasoning budget. Unsupported future model configurations can still
   fail and must be validated before use.
3. **Citation/context mismatch:** more source entries than the citation contract
   allowed caused valid responses to fail. Context now supplies at most four
   IDs; repeated valid IDs are normalized, and invented IDs still fail.
4. **Source starvation:** early chunks could exclude the second search from
   context. Round interleaving fixes that mechanical problem, but relevance and
   diversity are not fully solved.
5. **Browser request surface:** model-generated Markdown images could trigger
   browser requests. Shared chat image rendering is disabled; experimental
   answers additionally reject external resource output.
6. **OpenAI configuration:** after the owner replaced the key and explicitly
   approved the reference comparison, all twelve OpenAI comparison responses
   completed. The earlier payload review rejection was resolved by that approval.
   See the follow-up for the measured results. Live Claude behavior is untested.
7. **Teaching accuracy:** live Java equality and JavaScript storage claims were
   too broad. Prompt qualification alone did not reliably fix them. The follow-up
   added a conservative guard and verified that all four affected responses were
   withheld as uncited clarifications. This is not general factual verification.
8. **Retrieval completeness:** neither strategy found the expected arrays PDF in
   the linked-list comparison. Another source offered comparative information,
   but the exact-source target remains unmet.
9. **Answer protection is incomplete:** deterministic guards catch obvious code
   and external content, not every natural-language solution, fabricated claim
   or prompt-injection tactic. This is a controlled pilot, not a security proof.
10. **Unproven scope:** no large-corpus/concurrent-user load certification,
    independent learner study, comprehensive adversarial live evaluation,
    supported-provider parity, or production container certification is claimed.

These are reasons to retain the opt-in gate. Before wider use, evaluate more
multi-source and weak-source cases, include collection/version qualifiers in
editorial review, compare against a stronger deterministic retriever, and obtain
independent assessment of factual grounding and Socratic usefulness. Continuing
this evaluation does not require settling subscription or payment packaging.

## Reproducing the experiment

From `dsa-chatbot-api`:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python tools/evaluate_agentic_rag.py --provider gemini --cases 6 --output docs/agentic-rag-evaluation.json --live
```

The second command invokes the configured provider: at most 24 model calls and
14,400 output tokens across the two strategies. It does not rebuild embeddings,
modify approvals, execute submitted code or change learner balances. Provider
failures and unsuccessful debugging probes may still incur provider usage.

To try the HTTP pilot privately, set `AGENTIC_RAG_ENABLED=true`, restart the API,
and use an admin account's chat screen. The checkbox is opt-in. Remove the flag
or set it false to disable new pilot requests. Previously completed keyed
receipts remain replayable; disabling the flag does not erase conversation data.

## Verification

Initial pilot checkpoint: **474 backend tests passed**; the linked follow-up
records **486** after additional fixes. Frontend suite: **69 passed**. TypeScript,
production build, Python compilation and whitespace checks passed. One existing
LangGraph serializer deprecation warning remains.

Tests cover scope and ownership attacks, unknown tools/arguments, source
revocation and revision changes, citation forgery, code and external-content
withholding, repeated/invalid plans, empty retrieval, cancellation and deadlines,
context/call/token ceilings, SDK retry settings, API gate/replay/refund behavior,
ordinary-RAG compatibility, SQLite write-lock regression, and UI opt-in/image
protection.

Post-change upload audit: **38/38** expected-source questions pass. Live SQLite
integrity remains **ok**, with **zero ledger mismatches** and all **38** documents
still published. No embedding refresh, public deployment, source approval change
or commercial policy change was performed.
