# V1 learning product contract and gap map

Status: proposed product contract, 9 November 2026. This document defines the target for implementation and review. It does not change current progression, access, pricing, or claims about course quality.

## Product promise and scope

For every section offered to a student, the app must provide a coherent route from a stated starting level to a stated outcome: reviewed teaching material, independent practice, actionable feedback, a valid assessment, an application or transfer task, visible evidence of progress, and a justified next step. A reference page, problem count, or chat response alone is not a complete paid learning path.

V1 has one AI tutor and three sections: Language Fundamentals, DSA, and Design Patterns. Human tutor workflows, AI Tutor+, circuit programming, subscription packages, and prices are later decisions. The core tutor can constructively challenge reasoning when it has a sound basis.

## Shared learning contract

| Term | Meaning | Can it advance mastery? |
| --- | --- | --- |
| Seen | Student opened a lesson or example. | No. |
| Attempted | Student submitted work or answered a check. | No, by itself. |
| Assessment passed | A versioned task was scored against its published contract and passed. Record language, section, task/rubric versions, hints, and result. | Evidence toward mastery, subject to the section rule. |
| Mastered | Required reviewed assessment evidence plus an independent transfer or application check supports the named capability. | Yes, only through application policy. |
| Review due | Previously demonstrated capability needs a fresh check under a future review rule. | Does not erase historical evidence. |

These are **target states**, not labels for existing history. Today's `learning_path.progress()` sets `mastered = complete` when its existing exercise/check/coverage rule passes. The new mastery state must be added separately and migrated only from evidence that meets its new rule. Historical `complete`, `solved`, or chat events must not be silently upgraded. Until that implementation exists, UI and API wording must explain the current rule without claiming independent transfer mastery.

Prerequisite links initially **recommend** a sequence and explain gaps; they do not lock content or automatically grant or deny mastery. A student may browse ahead or take a diagnostic. The current node remains a navigation recommendation. A later change to unlocking or mastery would require a separate policy decision and migration plan. This resolves the inconsistency noted in `LEARNING_PATH_DECISIONS.md` as the target policy, without changing runtime behavior here.

### Student pathway choices

Start from a reviewed default path. Allow a goal, preferred language, relevant experience, application interests, pace, and requests for review or a diagnostic to influence recommendations. Keep the assessed capability and rubric stable. Skipping a lesson marks neither an assessment pass nor mastery. Record each path change with its reason, student choice or system recommendation, content version, and policy version. Permit the student to return to the default route.

### Section outcomes

- **Language Fundamentals:** understand and use language constructs and contracts in small programs; debug and explain behavior; transfer to a fresh task in that language.
- **DSA:** select and justify a technique, maintain its invariant, analyze complexity, implement it, test counterexamples, and transfer it to a changed problem.
- **Design Patterns:** recognize the design problem, decide whether a pattern is warranted, implement an idiomatic solution, explain tradeoffs, and defend a simpler alternative when appropriate.

Cross-section concepts use stable IDs and explicit typed links. Shared curriculum definitions are versioned and reviewed; each section retains its own teaching sequence and assessment rubric. An Assumption Ledger and Decision Log are **student records** linked to those concepts, not shared curriculum facts. Cumulative progress counts a shared capability once and shows the distinct evidence earned in each section.

## AI tutor and harness contract

The tutor must stay within the student's accessible section and selected task, use authorized learner-safe material, adapt its explanations to relevant recorded evidence, and distinguish a suggestion from an assessment. A challenge must have a reviewed source, a valid counterexample, or an executable test. The tutor should ask a focused question or give a direct explanation when requested; it must not manufacture objections or unsupported confidence scores. It must explain uncertainty and accept correction.

Application code enforces account and section access, tool permissions, solution visibility, task/rubric versions, and mastery transitions. Prompts and response checks handle teaching style and relevance. An AI-generated statement cannot itself write mastery. Store tutor actions and their basis separately from student-authored reasoning. The AI tutor dashboard should show actions, corrections, unresolved uncertainty, outcomes, latency, resource use, and estimated provider cost; these are operational measures, not tutor proficiency grades.

Use RAG for question-specific source retrieval, KAG for reviewed concept relations, and CAG for small stable action packs when measured results justify them. Keep student-specific data out of shared cached prefixes. Quality is a release threshold; optimize token, CPU, and memory cost within it. Evaluate factual accuracy, relevance, pedagogical usefulness, assessment validity, latency, and cost on the same cases.

## Access and release rules

Language selection and section entitlement are separate decisions. The future access policy must cover catalog listings, direct URLs, chat and retrieval, tutor tools, tasks, projects, recommendations, and dashboards. Cross-section links may describe a concept but cannot expose restricted lesson bodies or launch locked activities. Preserve student history when access expires. Define section access before designing packages or prices; current per-language subscriptions remain the live rule until an explicit migration.

Release a section for payment only after an end-to-end learner walkthrough, reviewed objectives and content, scored independent work, useful feedback, valid progress labels, access tests, and measured tutor quality/cost. Software coverage is necessary for enforceable rules but does not certify instructional quality. Record reviewer, content/rubric versions, sample cases, failures, and unresolved risks.

## Pilot gap map: one connected JavaScript route

This is an implementation map, not a claim that the three units are ready. Review the exact lesson and rubric content before declaring a prerequisite satisfied.

| Route | Existing anchor | Missing for a complete slice |
| --- | --- | --- |
| Language: functions, conditions, and functions as values | `learning_path.py` stages 2 and 4; `data/content/language/javascript-path-04-functions.md`; quizzes and exercises | Verify that a student can pass a function as a value and explain its input/output contract. Add a reviewed transfer check and distinct evidence state. |
| DSA: binary search | DSA catalog has `binary-search` tags and practice links; per-language solve events feed the overview | Author a technique route with sorted-input precondition, invariant, boundary counterexamples, complexity reasoning, graduated practice, and an independent transfer/application task. A solve count does not establish technique mastery. |
| Design Patterns: Strategy in JavaScript | Reference page, suggested order, and `docs/curriculum/STRATEGY_JAVASCRIPT_PILOT.md` | Review teaching and rubric, add callback-capable grading, accept a justified simple conditional, add transfer and misconception feedback, then expose a graded path. |
| Cross-section links | `data/curriculum/prerequisite-pilot.json` covers early language stages; pattern-related catalog links exist | Assign stable IDs and reviewed typed links among the three capabilities. Do not infer that the DSA technique is a prerequisite for Strategy. Test that links respect section access. |
| Records and profile | `LearningEvent`, language-path progress, DSA solves, and `study_progress.overview()` | Add per-section evidence and common state semantics, student path decisions, Assumption Ledger, Decision Log, and cumulative reporting without double-counting. |
| Tutor and access | Focused chat, Study Room, language access, prompt caching, and opt-in KAG/CAG pilots | Specify section-specific tutor behavior and evaluate it; enforce section access across every route and tool before selling section-specific plans. |

## Next implementation gate

Implement a small versioned concept/link schema and a section-access design against this route. First verify exact lesson coverage and audit all access entry points. Keep prerequisite edges advisory, preserve existing progress history, and leave current pricing and feature flags unchanged. Each code change then follows implementation, behavior verification, code review, targeted fixes, repeat verification, tests, final checks, commit, and push.

Related sources: `docs/PRODUCT_BASELINE_AND_DEVELOPMENT_PLAN.md` (existing untracked baseline), `docs/LEARNING_PATH_DECISIONS.md`, `docs/DESIGN_PATTERNS_COURSE_AUDIT.md`, `app/services/learning_path.py`, `app/services/study_progress.py`, `app/services/language_access.py`, `app/routers/tracks.py`, and `app/core/config.py`.
