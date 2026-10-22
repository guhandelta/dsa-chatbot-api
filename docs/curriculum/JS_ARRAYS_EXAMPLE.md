# Filled authoring example: JavaScript Arrays

Status: filled authoring example aligned with the published Arrays guided-activity bank.
These prompts are ungraded; task-specific independent grading fixtures remain to be authored.

## Capability

Use arrays to traverse and transform ordered values, preserve a stated mutation
contract, handle boundaries and justify a small algorithm. Required foundations:
variables, conditions, loops, functions, strict comparisons and basic testing.

Use finite JavaScript numbers for numeric tasks; exclude sparse arrays and NaN
unless a separate extension explicitly introduces them. State when the array may
be mutated. Do not silently change contracts between examples and tests.

## The 12-activity guided bank

| ID | Route | Learner task | Intended evidence |
|---|---|---|---|
| arrays-01 | Core | Trace push, pop and indexed replacement on a short dense array, writing the contents after each step | Operation order and state |
| arrays-02 | Extension | Compare truthiness filtering with removing only null | Precise predicates versus truthiness |
| arrays-03 | Core | Count readings strictly greater than a threshold; include empty input and equal readings | Direct traversal and boundary comparisons |
| arrays-04 | Core | Return a new array with one valid position replaced while preserving the original | Copying, indexing and a mutation contract |
| arrays-05 | Core | Define and implement how replacement rejects an out-of-range or non-integer index | Explicit failure behavior and input bounds |
| arrays-06 | Core | Remove null entries while retaining 0, false and empty strings, preserving order | Exact predicate versus truthiness |
| arrays-07 | Core | Find the length of the longest consecutive run strictly above a threshold | Applied state tracking and reset behavior |
| arrays-08 | Extension | Rotate a numeric array right by a nonnegative integer without changing the input; support k larger than its length | Empty-case handling and normalized position mapping |
| arrays-09 | Core | Diagnose why mutating a supposed copy changes the original, then state a correction and regression test | Reference reasoning and a test that checks input preservation |
| arrays-10 | Extension | Compare a filtering/mapping pipeline with a single traversal; count visits and temporary collections | Costs and readability, with an explicit cost model |
| arrays-11 | Core | Find the second-largest distinct finite number without sorting; return null if fewer than two distinct values exist | Independent transfer, duplicate handling and a maintained invariant |
| arrays-12 | Review | Later, solve a fresh ordered-reading task and explain its duplicate/mutation contract without notes | Retention and transfer, kept separate from unseen delivery |

Eight activities are core, three are optional extensions, and one is deliberate
review. Automatic review scheduling is a separate future feature. These are **guided activities**, not twelve ready-to-grade coding problems.
The count-above activity should link to the existing canonical
`javascript-path-06-arrays` exercise instead of duplicating its progress record.

## Example contracts to turn into full authored tasks

### Nonmutating replacement

Given a dense array, a valid integer index and a replacement value, produce a new
array with only that position replaced. Preserve the input. The later index-contract
activity defines invalid-index behavior explicitly rather than silently extending
the array. Keep nested object copying outside this first task's contract.

Tests should check the output, input preservation and whether the outer array is
new. A matching printed result alone does not establish the mutation contract.

### Longest run of readings above a threshold

For readings `[2, 8, 9, 1, 7]` and threshold `5`, the run lengths are `2` and `1`,
so the requested result is `2`. Equal-to-threshold readings break a run. Empty
input returns `0`. Tests should include all qualifying values, none qualifying,
one item, and the longest run at either end.

The task remains focused on arrays and a few scalar variables. It gives depth
before requiring Map, Set, sorting or an unfamiliar interview technique.

### Independent second-largest distinct value

State the finite-number precondition and the null result when no second distinct
value exists. Author cases covering empty input, one element, repeated maxima,
negative values and already ordered input. Ask for a trace or invariant that
explains how the maintained state changes. Put the reference implementation and
private tests in the author-only bank when the exercise is built.

Do not supply an almost-complete worked solution immediately before using this
task as independent evidence. A later activity from the same underlying family
can serve review, but should not inflate the count of independent capabilities.

## Readiness and onward routes

Suggested essential evidence: direct traversal, input preservation, empty/duplicate
handling, one applied state task, and a fresh independent task with a relevant
boundary explanation. A learner who struggles with aliasing should get targeted
reference/copy practice, not automatically repeat the entire array bank.

Onward composition choices:

- Arrays + Strings: normalization and grouping.
- Arrays + Objects: records, filtering and updates.
- Arrays + Set: reconciliation with preserved order.
- Nested Arrays: ragged collections and grid contracts.

Onward DSA choices: a small running-state task, then the guided invariant work in
Explain and independent variants in DSA Practice. Reuse canonical problem IDs.

## Language and framework adaptation

Keep the capability IDs but rewrite the contracts and examples for the destination
language's actual collection, copy and ownership behavior. For a framework profile,
translate the educational ladder into a native unit, such as updating collection
state or validating a collection input, with the required project fixtures. Do not
rename JavaScript syntax and assume it is an equivalent course.
