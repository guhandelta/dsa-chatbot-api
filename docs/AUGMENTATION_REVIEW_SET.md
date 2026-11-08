# KAG and CAG review set

Status: instructor review packet, 7 November 2026. These are review prompts, not certified learner assessments.

## KAG: does the added prerequisite help?

Use the current focused language chat and Study Room Explain mode. For each case, inspect the selected source IDs and the final answer. Rate the prerequisite as **helpful**, **unneeded**, or **misleading**. Confirm the answer stays on the selected language and does not present a pilot link as proof of mastery.

| Focus | Learner question | Expected graph behavior |
| --- | --- | --- |
| Python stage 7, maps | How do arrays prepare me for maps? | Include the stage 6 arrays lesson as optional reference. |
| Python stage 7, maps | How do maps work? | Keep a short graph hint; omit the full arrays lesson. |
| Python stage 7, maps | I'm stuck; can we review the foundation? | Include the arrays lesson. |
| Rust stage 8, sets | How does an array help me understand sets? | Include only Rust's stage 6 arrays lesson. |
| JavaScript stage 4, functions | Why is a function useful here? | Do not add the stage 1 values lesson unless the question calls for it. |
| Python stage 1, values | What is a value? | No prerequisite exists. |
| Python module, asyncio | Why await here? | Pilot graph does not cover this module; use current scoped retrieval. |
| Design Patterns reference, Strategy | When should I choose Strategy? | No language-stage KAG link; answer from pattern references only. |

Review the edge itself separately: *Would this concept actually help a learner understand the selected topic, or is it merely earlier in the course?* Replace or remove weak edges before extending the graph. The current word-based relevance rule can miss paraphrases; use the review outcomes to decide whether to improve that rule.

## CAG: compare with RAG-only before enablement

The version 2 Python and JavaScript packs are about 5K characters each. With CAG still off, compare answers to a short set of beginner, intermediate, and unrelated questions. Check factual accuracy, relevance, spoiler resistance, source scope, latency, and billed token cost. Include one cold-cache turn and repeated turns within the cache lifetime. A cache hit alone is not a success criterion; the earlier broad pack had cache hits and still cost more than baseline.

Do not turn on CAG globally from this local review. Choose a provider and call site only after the answer review and a separately authorized live comparison show value.
