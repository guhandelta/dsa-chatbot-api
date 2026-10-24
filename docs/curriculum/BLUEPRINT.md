# Reusable curriculum blueprint

Status: reusable authoring blueprint, 22 October 2026. Its first JavaScript
implementation now contains 29 lesson units and 180 guided activities: 96 basic,
56 combined and 28 DSA coaching activities. These are ungraded practice prompts;
they do not claim 180 new independently validated coding problems. Existing
assessment and mastery rules remain separate.

Use [the unit template](UNIT_TEMPLATE.md) when authoring a unit, and
[the Arrays example](JS_ARRAYS_EXAMPLE.md) as a filled example. A [JSON unit template](unit-template.json) mirrors the live activity fields. Task counts and
readiness thresholds below are starting product choices to evaluate with students,
not research-backed guarantees of proficiency.

## 1. Organize breadth and depth separately

The three tiers organize which ideas are combined. Each unit also has a practice
ladder that develops depth within those ideas. Students should not need a new
structure just to get a more demanding problem.

| Tier | Main question | Expected work |
|---|---|---|
| Basic structures | Can I understand and use this structure deliberately? | Trace operations, implement them, handle boundaries, explain mutation and equality, solve applied tasks, justify an approach |
| Combined structures | How should these structures cooperate? | Choose representations, preserve relationships and invariants, update nested state safely, compare alternatives, test and refactor |
| DSA foundations | Can I turn those skills into an algorithm and explain it? | Start with a trace and brute force, establish an invariant or recurrence, implement, test, analyze time/space and transfer to a fresh problem |

Programming foundations come first: values, conditions, loops, functions, error
contracts and the minimum testing skills needed to read feedback. Offer a baseline
check so experienced learners can demonstrate these prerequisites.

## 2. Practice ladder inside every structure

| Step | What changes | Array example |
|---|---|---|
| Understand and trace | Observe state and predict behavior | Trace updates to an array and identify its final contents |
| Perform operations | Write small, focused operations | Replace an element without changing the input |
| Handle contracts and boundaries | Reason about awkward but valid inputs | Empty arrays, duplicates, absent results and invalid indices |
| Apply the structure | Meet a small practical specification | Analyze runs of readings above a threshold |
| Diagnose and justify | Explain a defect or choose between approaches | Find an aliasing bug; compare traversal and allocation costs |
| Transfer independently | Solve a new variant with fewer prompts | Find the second-largest distinct reading under a stated contract |

Begin with a bank of approximately **12 authored activities per basic unit**:
8 core activities, 3 optional extensions and 1 deliberate review activity. At least one
extension should deepen the same structure without introducing an unlearned
algorithm. These are authoring targets, not a requirement that every student
complete every activity.

A unit should include tracing, implementation, debugging and reasoning. Avoid
building the entire bank from multiple-choice questions or repeated coding tasks
with only numbers or variable names changed. Grow the bank in response to gaps
in the skills it tests, not to maximize question count.

An activity may sit at more than one depth step, but should have one primary
learning objective. Specify difficulty with observable demands: number of moving
parts, unfamiliarity, edge cases, state changes, amount of scaffolding and required
justification. A harder task does not always need a faster algorithm.

## 3. Expand combinations by their teaching purpose

Do not generate the Cartesian product of all structures. Author a combination
when it introduces a useful modeling decision, relationship or failure mode.
Treat reversed nesting as another perspective within a family when appropriate,
not automatically as a second independent mastery achievement.

| Family | Useful perspective or task | Distinct skill |
|---|---|---|
| Arrays + Strings | Normalize, group or search collections of text | Collection order versus text normalization |
| Strings + Objects | Parse text into validated records | Parsing versus validation; absence versus falsy values |
| Objects + Map | Index records by stable identifiers | Identity, duplicate-key policy and shared references |
| Arrays + Objects | Filter records, summarize orders, update selected fields | Traversal plus mutation boundaries |
| Map + Set | Unique relationships per owner; later adjacency lists | Shared inner state and relationship uniqueness |
| Nested Arrays | Ragged data versus rectangular grids | Shape contracts and row/column bounds |
| Map + Array | Group events by key; chronological events within each group | Per-key collections, ordering and empty groups |
| Array + Set | Reconcile two lists of identifiers | Membership versus ordering; equality and duplicates |
| String + Map | Character or token frequencies under a text contract | Counting versus membership; normalization |
| String + Set | Distinct characters/tokens or allowed vocabularies | Explicit character units and membership semantics |
| Nested Maps | Index by region then product, or product then region | Access patterns and multi-level key ownership |
| Stack + String | Trace delimiters or a restricted expression format | Nested state; token rules before parsing |
| Queue + Map | Pending jobs with a lookup index | Keeping multiple representations consistent |
| Array + Objects + Map | A record collection with an index and an edit workflow | Synchronization, duplicate IDs and update contracts |

Use a small core route through the most useful combinations, then offer optional
routes such as text processing, record/data processing and stateful workflows.
Do not require every student to finish every combination before attempting easy DSA.

Within a combination family, author several perspectives:

1. Read and trace an existing representation.
2. Build it from raw input with an explicit contract.
3. Query it and justify why that representation fits the access pattern.
4. Update it while preserving its relationships.
5. Diagnose a realistic inconsistency or sharing bug.
6. Compare an alternative representation and explain a trade-off.
7. Transfer the model to a fresh scenario or small capstone.

Additional perspectives can become extension activities inside a unit. They do
not all need separate sidebar entries. This adds rigor without creating an
overwhelming course map.

## 4. Keep DSA teaching and DSA practice connected

Adding DSA problems is appropriate when each teaches or checks something specific.
The product already has a DSA practice area, so distinguish the experience:

| Explain: DSA foundations | DSA Practice |
|---|---|
| Small curated sets arranged by the concept being taught | A broader independent practice bank |
| Traces, brute force, invariants and worked reasoning | Transfer to unfamiliar statements and mixed techniques |
| Scaffolding that gradually fades | Optional hints, with assistance recorded |
| Compare approaches and explain why an optimization is valid | Implement, pass tests, revisit and improve solutions |
| A bounded learning route with an explicit next step | Continued breadth, repetition and challenge selection |

For an initial algorithm family, plan about **5–7 activities**: a worked trace,
a guided implementation, an edge-case/debug activity, two independent tasks,
an optional extension and a later review. Adjust the quantity when activities
overlap or student evidence shows more practice is needed. The current JavaScript
edition has four guided Explain activities per algorithm family; its existing
linked DSA problems provide independent coding practice without duplicate records.

Use one canonical problem ID, test suite and recorded solve per language. Link
that same problem from Explain and from the DSA practice bank. Presentation and
hint policy may differ, but navigating between sections must not create two solves
or two mastery awards for one accomplishment.

Label student-owned original practice separately from external problem references.
Keep provenance and source permissions as authoring metadata. There is no need to
reproduce the full breadth or branding of another platform to teach the foundations.

## 5. Reuse the structure across languages

Keep shared capability IDs, such as ordered traversal, key lookup, uniqueness,
record modeling, reference reasoning and nested-state consistency. Map those
capabilities to the actual constructs in each language.

Each language profile must specify:

- Native structure names and idioms, including when there is no direct equivalent.
- Runtime/toolchain version and supported execution environment.
- Value/reference and mutability rules; ownership and lifetime where applicable.
- Equality, ordering, hashing, missing-value and error contracts.
- Text encoding, indexing and normalization assumptions.
- Testing conventions, relevant costs and language-specific pitfalls.

Re-author examples and tests in that language. A JavaScript Object is not a
universal substitute for a dictionary, record or class in every other language.
Keep unsupported assessments explicitly unavailable until their harness and
fixtures exist. Do not serve foreign-language code as a fallback.

## 6. Adapt the same progression to frameworks

Reuse the educational pattern rather than forcing identical topic names:

| Level | Language pathway | Framework pathway |
|---|---|---|
| Foundations | Individual structures and operations | One framework concept at a time: components, state, routes, models, validation or lifecycle |
| Composition | Structures working together | Concepts working together: forms + validation, routes + permissions, state + effects, queries + transactions |
| Independent application | DSA foundations and algorithmic transfer | Bounded integration/design tasks, refactoring, performance reasoning and realistic debugging |

Select a coherent framework profile; not every row applies to every framework.
For a UI framework, a core-to-composition-to-application route could be component
inputs → stateful forms → a tested data-driven interface. For a backend framework,
it could be request handling → validation and persistence → a tested transactional
workflow with permissions and explicit failure behavior.

Framework exercises require reproducible project fixtures: dependency versions,
configuration, setup, tests and a clear environment reset. A bare snippet may be
enough for tracing, but is often insufficient for a graded integration task.
Pin documentation versions when authoring. Introduce language prerequisites before
framework-specific behavior and teach the distinction between them.

HTML/CSS profiles should use markup/layout/component composition and practical
interface tasks rather than pretending they need the same algorithmic endpoint.

## 7. Progress and completion evidence

Track these separately:

- **Exposure:** a lesson was opened or discussed.
- **Assisted practice:** a learner completed work with hints or a worked example.
- **Independent application:** a fresh task passed under its authored contract.
- **Retention review:** a later task or explanation supports remembering the idea.
- **Transfer:** a fresh representation, scenario or composition was handled.

A suggested initial readiness rule is: meet the unit's essential capabilities,
pass two distinct fresh application tasks and explain one relevant boundary or
representation choice. Add test evidence where execution is supported; retain
rubric/reviewer evidence for explanation and design work. Validate this rule with
real usage rather than presenting it as a proficiency standard.

Completion must not depend only on messages sent, examples viewed or raw question
count. Do not force a new learner to finish all optional extensions. An experienced
learner may demonstrate prerequisites through a fresh diagnostic task. Additional
practice can target the specific missed capability.

The current app exposes deliberate review activities; automatic due-date scheduling is still planned.
Keep unseen practice and deliberate review separate. Repetition belongs in an
explicit review queue; cosmetic variants should not count as independent evidence.
Store content versions so publishing additional exercises does not erase prior
accomplishments or silently redefine a completed unit.

## 8. Authoring and publication workflow

1. Specify the learner capability and prerequisites before drafting tasks.
2. Choose a core route and optional perspective routes.
3. Author distinct task families with contracts and expected behavior.
4. Attach hints, feedback and a rubric to the intended misconception.
5. Validate reference behavior, boundary tests and the intended failure for bugs.
6. Review language/framework ownership and source provenance.
7. Publish only ready material; keep planned or missing content marked honestly.
8. Observe where students stall, where hints reveal too much and where tasks repeat.
9. Refine the bank and readiness rules using that evidence.

Use the same tagged activity across Explain, quizzes, debugging and DSA only when
its purpose fits. Keep private answers/tests separate from learner payloads. The
authoring template is a specification, not a claim that all its progress states
or publication controls are already implemented by the app.

## 9. Useful additions to plan explicitly

- A learner-authored trace, test case or explanation before an automated hint.
- Fading scaffolding: worked example → partial guidance → independent transfer.
- Contrast cases: correct code, incorrect code and two valid designs with different trade-offs.
- Small capstones that combine a few learned ideas without requiring a full application.
- Testing and debugging integrated from early units, not reserved for an advanced tier.
- A misconception map that points to a relevant explanation and a different practice family.
- Accessibility: usable text descriptions, keyboard navigation and feedback that explains failures.
- Quality metrics: independent transfer, retention, helpful feedback and duplicated task families,
  alongside content counts and completion percentages.

The next assessment milestone should be **one basic unit and one combined unit
with fully validated independent assessments**, reviewed end to end. The guided
activity banks supply the practice sequence; they still need task-specific grading
fixtures before they can certify those additional capabilities. Use reviewed
assessment profiles before scaling grading across languages and frameworks.
