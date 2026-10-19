# Study Room reliability patches and separate curriculum work

Agreed scope, 2026-10-19.

## Current patches

1. Reserve mentor hint tiers with billing before generation. Keep only the
   billing facts needed for pricing and reward eligibility when learning-profile
   reasoning and quiz answers are erased. Reject a request if its current price
   exceeds the price the student accepted.
2. Bind Study Room conversations to their focus and comparison language. Ignore
   replies from superseded UI contexts. Preserve final quiz results while the
   learning path refreshes.
3. Restrict quizzes to the focused node's level ceiling. Exclude imported
   questions whose difficulty is unknown. Report missing lessons, exercises and
   assessments explicitly; do not claim incomplete curricula are launch-ready
   or finished.

These are reliability and reporting changes. They do not certify the pedagogical
quality or prerequisite alignment of the existing material.

## Separate workstreams

### Language and framework curricula

Author and review each language and framework deliberately. For each stage,
record learning objectives, prerequisites, worked examples, misconceptions,
practice tasks, assessment rubrics, feedback and progression criteria. Check
examples and reference solutions by execution where possible. Verify both
correct and incorrect answers. Review cognitive load and prerequisite alignment,
not just difficulty labels or question counts. Complete and validate one language
at a time; decide the language order before starting that content project.

Framework paths need their own learning objectives and prerequisites rather than
inheriting the language path mechanically. Framework version and runtime support
must be explicit. Reusing knowledge-base rows still requires mapping and review.

### DSA exercises and design-pattern pathways

Treat these as separate authored pathways, each with its own progression,
worked examples, practice and assessment review. Link them to prerequisite
language concepts without conflating the paths.

### UI development workspace

Provide a dedicated learning and practice view for UI frameworks. Define editor,
preview, error feedback, interaction checks and accessibility assessment in its
own design. Specify the supported frameworks, versions and execution model
before implementation. Preserve the learner's curriculum context across views.

### Circuit-programming workspace

Provide a separate view for Python, C and C++ circuit programming. Define target
boards and runtimes (including whether Python means MicroPython or CircuitPython),
board/pin views, wiring, simulation or device execution, serial output and
hardware-specific assessment. A generic language runner does not establish
circuit-programming support. Choose and validate the execution approach in that
separate project.

## Rollout

Apply migrations `0014_hint_billing` and `0015_study_thread_focus` before serving
the patched API. Existing hint events are backfilled into minimal billing
history. The new browser price cap is optional for older clients; updated clients
supply it for mentor and practice hints. Restart the API after migration. Neither
migration is applied to the user's running database by this patching task.
