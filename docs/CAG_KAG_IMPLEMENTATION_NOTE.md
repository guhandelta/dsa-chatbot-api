# CAG and prerequisite-graph implementation note

Status: six-call live pilot completed, 7 November 2026. Production CAG enablement is pending.

## What exists

- Prompt assembly places stable instructions first. Claude receives an explicit cache breakpoint when `PROMPT_CACHE_ENABLED=true`; OpenAI and Gemini receive a stable-first string and depend on provider-side caching behavior.
- CAG is implemented behind `CAG_ENABLED=false`. Compact version 2 Python and JavaScript context packs are limited to Claude by default. The loader strips protected material, enforces a size cap, and requires a pinned SHA-256 digest. Question-specific RAG remains separate.
- `data/curriculum/prerequisite-pilot.json` defines a small, acyclic learning-dependency graph for shared stages 1–8. Focused language RAG now adds at most two linked, same-language prerequisite lessons from the local answer-safe catalog and labels them as optional guidance. It is not used for mastery or unlocking. It is off by default; `KAG_ENABLED=true` turns it on, and leaving it unset keeps the former retrieval path.

Local coverage check: all ten current language paths have authored lessons for the first eight stages. Each path's seven non-root pilot nodes resolved its linked prerequisite lesson. This proves link resolution, not that every edge is the best teaching prerequisite. Focused chat traces now record graph version, linked IDs, and the linked source IDs actually used, without storing lesson text.

KAG now also supplies optional prerequisite guidance in Study Room Explain mode. Full linked lesson text is added only when the learner mentions the earlier concept or asks to review because they are stuck. This word-based rule is intentionally narrow and can miss paraphrases. Use the [review set](AUGMENTATION_REVIEW_SET.md) to judge the teaching value of each edge and the relevance rule before expanding it.

## CAG pilot gate

1. Inspect the exact outgoing prompt and pack before any provider call. Do not include credentials, learner history, private uploads, hidden tests, or protected answer sections in a reusable pack.
2. Run `python tools/measure_prompt_cache.py --language python --problem two-sum --turns 2` only after explicit approval to send repository-derived content to Anthropic. The command makes six paid calls: two each for baseline, cache-only, and cache-plus-CAG. It does not change persisted settings.
3. Record per-call input, cache creation, cache read, uncached input, output tokens, model, latency, and response validity. Compare **total billed cost**, not just cached-token count; a first cache write can cost more than an uncached request. Repeat with realistic turn spacing and a second problem before claiming typical savings.
4. Check that CAG does not cause irrelevant or stale lessons to dominate a narrow question. Compare against RAG-only answers on a reviewed set of questions. Keep CAG off if quality worsens, the pack fails its hash, or cache reuse is too low.
5. Pilot by explicit language and provider allowlist. Version the pack whenever its source changes. Do not bulk preload the retrieval index.

Local payload inspection for the two-sum pilot found no API-key pattern, private-key marker, email address, or protected answer heading. This is a limited pattern scan, not a guarantee that arbitrary future content is safe to export.

### Six-call result (Claude Sonnet 4.6, version 1 broad pack)

| Configuration | Input tokens | Cache reads | Cache writes | Output tokens | Mean model latency | Estimated token cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 959 | 0 | 0 | 148 | 2,752 ms | $0.00510 |
| Cache only | 957 | 0 | 0 | 133 | 2,565 ms | $0.00487 |
| Cache + CAG | 13,051 | 12,542 | 0 | 115 | 2,357 ms | $0.00701 |

Both CAG turns reported 6,271 cache-read tokens, including the first turn. The cache was therefore already warm at measurement time; this run did not measure a cold cache write. All six returned tutor replies contained exactly one question. The CAG configuration was about 38% more expensive than the short baseline prompt *even with full cache hits*, because the extra 6,271-token prefix still incurs cache-read charges. These are token-cost estimates at Claude Sonnet 4.6's published $3/M input, $15/M output, and $0.30/M cache-read rates; they exclude other billing modifiers. Two turns on one problem are insufficient for a quality or latency claim.

Decision from this pilot: keep CAG disabled by default. Version 2 packs are now about 4.8–5.1K characters, down from about 21K; their quality and economics have not been measured with live calls. Compare them with scoped RAG before enabling. The cache-only flag is already enabled, but its short mentor prefix produced no cache reads in this run.

Local version 2 check: Python and JavaScript each load a three-file pack with a Claude cache marker; neither rendered pack contains protected solution or hint headings. The app's Claude trace estimate now applies five-minute cache write and read rates instead of treating cached tokens as full-price input. A live comparison and instructor-reviewed answer set are still needed before turning CAG on.

## KAG contract before wiring retrieval

Here KAG means knowledge-augmented generation using a curated prerequisite graph, not a second unstructured corpus. Use stable concept IDs, typed `requires` edges, versioned source references, and an acyclic graph. The pilot graph currently covers only the shared first eight stages.

At question time, resolve the active course node, fetch at most its direct prerequisites and the requested node's reviewed content, then apply the same language, authorization, and answer-safety filters as ordinary RAG. The first integration applies this only to a focused language chat whose focus resolves to an authored stage exercise. It leaves the vector query pinned to the selected item and draws linked lessons from the local learner-safe catalog. Graph version and linked source IDs are now in traces. If a node or edge is missing, fall back to the current scoped retrieval path; never broaden to another language or treat an unresolved edge as mastery evidence.

The graph should support **recommendation** first. Unlocking and mastery require a separate product decision. `progress()` currently calculates each node's completion independently despite a comment saying prerequisites block later stages; reconcile that before using graph edges to gate learners. Evaluate KAG against RAG-only retrieval for relevance, citation correctness, latency, and whether the prerequisite is actually needed. Expand edges only after an instructor reviews the first route.

## Remaining decisions

- Run a cold-cache measurement and a reviewed answer-quality set after narrowing the pack; obtain separate approval for any additional live calls.
- Review the JavaScript course and decide whether graph edges recommend, unlock, or affect mastery.
- Choose the next language pack after the Python/JavaScript pilot; each pack needs its own source review and quality evaluation.
