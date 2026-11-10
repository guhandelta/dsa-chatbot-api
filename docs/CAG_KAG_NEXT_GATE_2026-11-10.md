# CAG and KAG: next release gate

Status: preparation, 10 November 2026. CAG and KAG remain off by default. This document records what can be verified now, what must be authored, and what evidence is needed before a narrow rollout. It does not certify teaching quality.

## Current structural inventory

| Language | Existing path nodes | Nodes with existing coverage rule satisfied | Available checks | Pilot KAG source gaps |
| --- | ---: | ---: | ---: | ---: |
| JavaScript | 18 | 18 | 176 | 0 |
| Java | 17 | 17 | 159 | 0 |
| Python | 20 | 20 | 185 | 0 |

These figures come from `learning_path.nodes()` and `prerequisite_graph.audit_language()` on the current repository. Coverage means the app sees the required files and checks under its current rule. It does not establish the correct sequence, task validity, independent transfer, or that a student learned the concept.

## Order of work and gates

1. **Author three native route specifications.** For JavaScript, Java, and Python, define the intended learner, starting knowledge, outcomes, topic order, language-native structures, prerequisite explanations, practice ladder, recovery, small applications, and independent evidence. Use a common unit schema but no automatic topic translation. Audit links and worked examples; leave unreviewed routes in draft state. The current JavaScript Arrays evidence pilot identifies missing independent choice and transfer checks.
2. **Assess KAG links.** For each authored edge, record why the earlier concept is necessary or helpful, its source lesson/version, and at least one question where the edge should *not* be inserted. Validate IDs, order, cycle freedom, same-language and answer-safe sources. Use the eight current cases as a baseline, then add cases tied to the three authored routes. Compare RAG-only and KAG-assisted answers for correctness, relevance, learner level, and unwarranted mastery/weakness claims. Remove misleading edges. Keep graph failures on the scoped RAG fallback.
3. **Assess compact CAG packs.** For each language and tutor action, record the exact pack file list, rendered SHA-256, size, stable prompt, dynamic tail, and allowed provider. Compare RAG-only, cache-only, and cache+CAG on the same beginner, intermediate, and unrelated questions. Include cold and warm calls, token categories, total estimated and billed cost, latency, spoiler checks, and factual review. Stale or oversized packs must be skipped. Do not share student state in a cached pack.
4. **Assess combinations.** Compare RAG, RAG+KAG, RAG+CAG, and RAG+KAG+CAG only where the content and focus make both additions applicable. Predefine the pass rule: no critical factual, access, or answer-safety regressions; improved or equal teaching usefulness; and an explicit cost/latency tradeoff. Evaluate answer text, not source selection alone. A narrow call-site/language allowlist is preferable to a global flag.
5. **Roll out and observe.** Keep both flags off until the evidence and authorization gates pass. Turn on one language and action at a time, monitor traces, corrections, latency, fallback, and cost, and retain the ability to disable each enhancement independently. Revalidate when lessons, graph edges, pack hashes, models, or prices change.

The existing `tools/measure_prompt_cache.py` is a six-call live test with `--turns 2`; it tests one mentor problem and three cache configurations, not the four RAG/KAG/CAG combinations above. New live prompts and repository-derived content require their own payload review and authorization. Do not represent a dry run, stubbed model, or six-call cache result as full tutor-quality evidence.

## Inputs still needed from the product author

- For each language: target audience, entry diagnostic, intended outcomes, supported runtime/version, native topic order, and reasons for each prerequisite edge.
- Lesson examples and source references with provenance and permission to use them; known language-specific pitfalls and counterexamples.
- For each unit: ordinary and boundary exercises, private expected behavior/tests, accepted alternative solutions, hint stages, misconception-specific recovery, an application/project brief, and an unrelated transfer task.
- Assessment rubrics and sample correct, partially correct, and wrong responses, including cases where code passes but reasoning is weak. Define what assistance prevents an independent pass.
- A labeled evaluation set of actual or realistically simulated learner questions: relevant, unrelated, confused, paraphrased, adversarial, and cross-section cases, with expected source scope and quality criteria.
- A policy for student data retention/consent if real submissions or chats are used to improve the tutor, and explicit authorization for any new live provider payload. Provider budget and acceptable quality/cost tradeoffs must be set before a live comparison.
- Section entitlement/grandfathering decisions before paid section-specific rollout.

The app can use these inputs through authored curriculum, retrieval, context packs, prerequisite graphs, and evaluations without training new model weights. Fine-tuning would be a separate decision with its own data quality, privacy, and measurement requirements.
