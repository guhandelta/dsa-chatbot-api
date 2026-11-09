# Connected tutor evaluation pilot

Status: offline reviewer set, 9 November 2026. No model calls or quality certification have been performed for this set.

`data/evals/connected-tutor-pilot.json` contains five focused questions spanning JavaScript functions, binary search, and Strategy. Each case names its section, language, catalog focus, expected teaching points, and likely failure modes. Run `.venv/bin/python tools/validate_connected_tutor_eval.py` to check that every focus resolves to its declared section. This validation checks structure, not answer quality.

Before a live comparison, a qualified reviewer should confirm the questions, expected points, and acceptable alternative explanations. For each candidate route (current retrieval, selective KAG, narrow CAG, useful combinations), present the same cases without showing the reviewer which route generated each answer. Record factual correctness, relevance, pedagogical fit, unsupported claims, completeness, and whether a learner could act on the answer. Keep the response and source IDs for audit, but never interpret keyword overlap as a passing quality score.

Measure prompt and completion tokens, cache reads and writes, estimated provider cost, end-to-end latency, local CPU and peak memory, and any extra follow-up needed to repair confusion. Compare cost per useful learning interaction, not only per call. Do not turn on KAG or CAG from cache hits alone. This five-case draft is too small to certify production behavior; broaden it with reviewed examples, adversarial requests, and real learner follow-up before a release decision.

The earlier authorization covered six specific Claude test prompts. It does not authorize new live provider calls for this evaluation. The local validator and tests make no network calls.
