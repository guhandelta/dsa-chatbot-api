# Section access design for the v1 learning paths

Status: design only, 9 November 2026. Current per-language subscription behavior remains in effect. This document is an implementation checklist, not an entitlement grant or a pricing decision.

Implementation update: `section_entitlements` and `section_access.require_section()` now provide a separately migrated, testable candidate decision for section rights. The function checks the existing language scope first, then active section dates. `compare_access()` reports the legacy and candidate decisions for an offline audit; it does not write grants or change live access. It is **not wired to learner endpoints**, and no section entitlement has been inferred or backfilled from an old subscription. The live access rule is unchanged. Before activating the new policy, complete the endpoint/tool matrix below and choose an explicit grandfathering rule for existing students.

## Policy boundary

The future decision is `can_access(user, section, language, action)`. It must be evaluated in application code before reading protected content, retrieving tutor context, running an assessment, or writing a progress event. Language access and section access are separate: access to JavaScript does not imply access to all JavaScript DSA or Design Patterns activities. `algorithm` is an internal catalog track mapped to the learner-facing `dsa` section.

An active student needs both a permitted language and a permitted section for an activity. An expired section entitlement blocks new learning actions while preserving history. Admin access and any future instructor role policy are separate explicit branches; human tutor workflows are outside v1. No model prompt may grant access. No peppercorn balance substitutes for an entitlement.

The current `Subscription` table is per language and `allowed_languages()` grants language scope. Section entitlements need an explicit data model and migration before activation. A candidate is a versioned entitlement row with user, section, optional language scope, status, start/end, source, and audit timestamps. Do not reinterpret existing subscription rows as paid section rights or infer a new plan from old billing records. Before switching the gate, define a deliberate grandfathering and expiry policy and test it with historical users.

## Access matrix to implement and test

| Surface | Required check | Cross-section behavior |
| --- | --- | --- |
| Section list and counts | Return accessible sections and separately labelled locked sections. | Counts must not expose protected titles or assessment details. |
| Catalog item and direct URL | Check section and language before returning item body. | A linked locked item is represented as a locked reference, not a readable lesson. |
| Search, RAG, KAG, CAG | Filter candidates by section, language, review state, and answer safety before context assembly. | Graph edges never bypass an entitlement; shared packs contain no private student state. |
| AI tutor and Study Room | Check the requested section and every tool or source it opens. | Tutor may describe a shared concept at the current section's depth without assigning locked work. |
| Practice, code execution, quizzes, projects | Check section and language at task start and submission; recheck on delayed work. | A locked task cannot be reached through a recommendation or old deep link. |
| Solutions and hidden tests | Preserve existing solution-release rules after access checks. | No cross-section solution leak through a related-item endpoint. |
| Recommendations and pathway edits | Return actionable items only when accessible; mark other paths locked without exposing detail. | Never count browsing a cross-link as mastery. |
| Progress and profile | Permit an account to see its own retained history under a defined privacy rule; distinguish historic work from currently available actions. | Shared capabilities are counted once in the cumulative view, with section evidence shown separately. |

Current entry points requiring an audit include `/tracks`, `/problems`, `/study`, `/mentor`, `/analyze`, retrieval services, and any route that returns content metadata or solution access. The present `require_content()` checks language scope; it does not implement independent section rights. UI hiding is insufficient because direct API requests remain possible.

## Rollout and failure behavior

1. Inventory every endpoint and background job that reads content or writes learning evidence. Add a section identifier to task and event contracts; resolve internal `algorithm` to `dsa` centrally.
2. Build and test one policy function against a matrix of active, expired, missing, and multi-section rights, plus admin and suspended accounts. Keep it independent of billing plan names.
3. Apply the policy at service boundaries, then at endpoint entry points. Recheck for queued work. Make absent or malformed rights deny the protected action, with a clear error for the student.
4. Add API integration tests for direct links, cross-links, tutor retrieval, tasks, solutions, expiry, restoration, and retained history. Add UI tests for the corresponding student states.
5. Migrate historical access deliberately, run in report-only mode to compare old and proposed decisions, inspect differences, then switch the gate only after the chosen grandfathering rule and product terms are settled.

Do not sell section-specific plans until the section's learning route meets the [product contract](V1_LEARNING_PRODUCT_CONTRACT.md) and this access matrix passes. A policy test proves enforcement; it does not certify the educational value of the section.
