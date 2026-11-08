# Learning pathway decisions and quality gate

Status: working proposal, 7 November 2026. This document does not change live progression.

## Current behavior to preserve until reviewed

The shared spine has 12 stages. A stage is marked complete when it has a stage-specific lesson and exercise, the learner passes the exercise, scores at least two thirds on checks, and has no open strike. A depth module requires a lesson and checks. Static coverage currently reports 18 of 18 JavaScript nodes and 20 of 20 Python nodes ready, but that does not certify factual accuracy, instructional sequence, or assessment quality.

The code comment in `app/services/learning_path.py` says missing prerequisites block later stages; `progress()` currently computes each node's `complete` value independently. The current node is the first incomplete node, but later nodes may still report complete. Decide whether prerequisites control *recommendation*, *unlocking*, or *mastery* before changing this behavior.

## Proposed mastery model

1. Keep `assessment_passed` as raw evidence: a passing executable exercise plus the required checks. Record when the evidence was earned and whether hints were used. Do not call a reference reading or chat turn an assessment.
2. Use `prerequisite_ids` only to recommend the next lesson initially. Permit an experienced learner to take a diagnostic check for an earlier topic. Do not make the pilot graph a hard gate.
3. Keep `mastered` distinct from `assessment_passed`. Mark mastery only when coverage is reviewed, the required evidence passes, and a fresh transfer task is completed without revealing the answer. Set an explicit review interval before adding spaced recall to the rule.
4. Show `content incomplete`, `ready for assessment`, `assessment passed`, and `mastered` as distinct learner states. Missing content must never be displayed as learner failure.

These thresholds need instructor review and learner testing before becoming product policy. Existing historical passes must not be silently upgraded to the new mastery state.

## First course quality gate: JavaScript

Use JavaScript as the first end-to-end review because it has a complete structural path and a more detailed unit blueprint. For each stage, verify the objective, prerequisite, worked example, at least one independent practice task, wrong-answer feedback, executable reference, and graded check. Review the first eight stages against `data/curriculum/prerequisite-pilot.json`. A passing schema or fixture test is necessary but does not establish teaching quality. Record instructor findings per stage before claiming the course is complete.

The pilot graph is learning metadata only. Its first eight edges are versioned separately and checked for valid, earlier stage references. Add later stages and language-specific depth modules after reviewing the first route with learners.

## Separate course work still required

| Pathway | Teaching goal | Course evidence still needed |
| --- | --- | --- |
| Language fundamentals | Learn a language's syntax, data model, idioms, and standard library | Language-specific objectives, worked examples, independent practice, reviewed checks, and versioned sources |
| DSA techniques | Recognize and justify approaches such as two pointers, binary search, and dynamic programming | Concept sequence, invariants, counterexamples, applied problem links, and transfer assessments |
| Design Patterns | Choose or reject a reusable software design based on its trade-offs | Pattern-specific prerequisites, idiomatic examples per language, anti-examples, refactoring exercises, and reviewed assessments |

The Design Patterns catalog is a reference section today, not a graded pathway. Do not treat retrieval coverage or the KAG pilot as completion of any of these courses. Maintain separate source review and learning outcomes for each; link between pathways only through explicit concept IDs after the teaching sequence is reviewed.

The Design Patterns reference section now uses `data/curriculum/design-patterns-reference.json` for a suggested reading order. Its only explicit link is the JavaScript shared-instance extension after the general shared-instance lesson. This sequence organizes reading; it does not declare the other patterns mastered, establish their language prerequisites, or certify the generated-gap-fill lessons. Instructor review should determine the eventual graded sequence and the examples and assessments for each supported language.
