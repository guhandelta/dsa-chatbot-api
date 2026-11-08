# Strategy in JavaScript: pilot exercise and assessment contract

Status: authoring draft, 7 November 2026. This file is outside the learner content catalog and awards no progress or mastery.

## Capability and prerequisites

The learner can pass a function to choose interchangeable behavior, preserve a clear input/output contract, and explain when a local conditional would be simpler. Prerequisites are JavaScript functions, parameters, return values, and conditionals. The existing language stage 4 covers function calls; an instructor must confirm the learner has also met a passing-functions-as-values example before assigning this exercise.

## Learner-facing challenge

An application produces notifications in several formats. Implement:

```javascript
function prepareNotification(event, formatter) {
  // Your code here.
}
```

`event` is a plain object. `formatter` is a function selected by the caller. Call it exactly once with the same `event` object and return its string result. Reject a result that is not a string with a `TypeError`. Do not edit `event`, inspect the formatter's name, or select a format inside `prepareNotification`.

Example callers may choose a short-text formatter or a JSON formatter. The exercise does not prescribe either formatter's implementation. The challenge is to keep notification preparation independent of the format choice.

After implementing it, answer two questions in words:

1. Who chooses the format, and what part of the code needs to change to add a third format?
2. If this application had one fixed format used in one place, would passing a formatter help or complicate it? Explain.

## Instructor-only behavior checks

The current generic function grader accepts JSON arguments and cannot pass a callback as an argument. These checks need a dedicated, isolated JavaScript harness before the exercise can go live. They must not be placed in learner retrieval or represented as an existing app assessment.

| Case | Expected evidence |
| --- | --- |
| Text formatter | Callback receives the same object once; returned text is passed through. |
| Alternate formatter | Same implementation accepts a different function and returns its different text. |
| Stateful callback | Closure state proves exactly one call per invocation. |
| Non-string result | `TypeError` is thrown; no invented fallback string. |
| Caller object | Object identity and fields remain unchanged. |
| Known bad: hard-coded formatting | Rejected by the alternate formatter and call-count checks. |

## Design rubric

For a pass, require all three forms of evidence: correct behavior on the callback checks; a clear explanation that the caller owns selection and new formats need not change `prepareNotification`; and a justified choice of a simpler direct call or conditional for the one-fixed-format scenario. A code-test pass alone is **behavior evidence**, not pattern mastery. Record assistance separately. The later transfer task should use another domain, such as a shipping quote or report exporter, without naming Strategy in the prompt.

## Feedback by failure

- Callback never called: ask which part of the contract supplies the format decision.
- Callback called twice: ask whether formatting can have side effects, and trace one invocation.
- Event copied or mutated: point to the identity-preservation requirement.
- Fixed branch inside the function: ask what changes when a new formatter is added.
- Overuses Strategy for the fixed case: ask what concrete variation justifies the extra indirection.

## Publication gate

Before publication, add a callback-capable execution path inside the existing code sandbox, prove that it rejects known-bad implementations, and review the task, examples, and rubric with an instructor. Keep it in draft until the app can distinguish a behavior check from a reviewed design decision.
