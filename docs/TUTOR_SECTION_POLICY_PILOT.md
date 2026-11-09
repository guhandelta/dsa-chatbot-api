# Section-aware Study Room pilot

Status: local guardrail and retrieval change, 9 November 2026. This is not a certification of tutor accuracy or a graded Design Patterns pathway.

When a Study Room explanation focuses on a catalog item, its catalog track now determines the learner-facing section: `algorithm` and `dsa` map to DSA; `design-patterns` stays Design Patterns; language nodes and reference subjects stay Language Fundamentals. The local answer-safe search uses that section and the selected item ID. This prevents a focused Strategy or binary-search question from filling its context with unrelated language lessons.

The explanation prompt adds a short section policy. Language prompts emphasize behavior and contracts; DSA prompts emphasize preconditions, invariants, boundaries, and complexity; Design Patterns prompts emphasize design pressure, tradeoffs, and a simpler alternative. All modes retain the existing solution and untrusted-context rules. An explanation response that explicitly awards mastery is replaced before its takeaway can be saved. This is a narrow guard for a specific unsupported claim, not a general factuality filter. Formal mastery remains in application assessment policy; no mastery rule or reward is changed here.

Next review: evaluate real responses for relevance, false objections, omissions, and appropriate challenge across reviewed cases in all three sections. Add an explicit assessment rubric for Strategy before offering graded progress. Section entitlements from `SECTION_ACCESS_DESIGN.md` are still design-only; existing per-language access remains the live gate.
