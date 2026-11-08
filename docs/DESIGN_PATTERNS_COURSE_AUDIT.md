# Design Patterns course audit and first unit draft

Status: authoring draft, 7 November 2026. This does not change learner mastery or publish a graded course.

## Current reference coverage

The catalog has 12 general pattern pages and one JavaScript-specific extension. The suggested order is stored in `data/curriculum/design-patterns-reference.json`. Ten general pages carry `review_status: source_linked_not_expert_certified`; the authored pages have no recorded independent instructional review in their front matter. The pages mainly offer a problem statement, when to use the pattern, when not to, language notes, and watchouts. None supplies a stage objective, worked trace, independent graded exercise, assessment rubric, or delayed transfer check in the app's Design Patterns pathway.

This is enough for a **reference reading list**. It is not evidence that every pattern has been taught or mastered. The JavaScript shared-instance page is an extension of the general page, not a separate mastery achievement.

## First pilot unit: Strategy in JavaScript

- **Unit ID:** `pattern:strategy:javascript:v1`
- **Status:** drafting; instructor review and runtime checks pending
- **Capability:** Given a small design problem, decide whether to pass interchangeable behaviour as a function or keep a straightforward conditional, and justify the choice.
- **Prerequisites:** JavaScript functions and parameters, calling a function, basic conditionals, and one focused example of passing a function as a value. Link these to authored language nodes after checking the exact lesson coverage.
- **Exclusions:** This unit does not assess class hierarchies, dependency injection frameworks, asynchronous scheduling, or pattern memorization by name.

### Teaching sequence

1. Start with a checkout calculation whose discount policy can vary by caller. Show the repeated branch and ask who owns the choice.
2. Trace a tiny `checkout(total, discount)` function with two supplied discount functions. Require the learner to predict both outputs and explain that the checkout function invokes its argument.
3. Contrast a one-off two-branch function. Ask whether extracting a strategy would make that code easier to read or change; accept a clear argument for keeping the conditional.
4. Guided practice: replace a growing central branch with a passed function while keeping input and output contracts explicit.
5. Debug case: a caller passes a function that returns an invalid value. Ask the learner to locate the contract boundary and describe how the app should report failure.
6. Independent transfer: choose a formatting or shipping policy for a new workflow without copying the checkout example. Include at least one case where a simple conditional is the better answer.
7. Later review: revisit the choice in a different language and explain which language feature carries the interchangeable behaviour.

### Worked example to validate

Assume `total` is a non-negative number and each policy returns a non-negative final price no greater than `total`.

```javascript
function checkout(total, pricePolicy) {
  return pricePolicy(total);
}

const fullPrice = total => total;
const tenOff = total => Math.max(0, total - 10);

console.log(checkout(30, fullPrice)); // 30
console.log(checkout(30, tenOff));    // 20
```

Trace which function the caller passes and what value comes back. The example is deliberately small: passing a function is the concept. A production checkout would validate totals and policy results at its boundary, which is the later debug task.

For independent transfer, give learners a separate notification-formatting task with two output formats and an explicit contract. Ask them to choose between a passed formatter and a local conditional, implement their choice, and justify why it fits the stated change frequency and caller ownership. The reviewer must accept either design when the reasoning and behaviour match the contract.

### Draft assessment gate

Pass only when the learner can (a) identify who selects the behaviour, (b) implement a working function-based choice under a stated contract, (c) give one reason to use it and one reason not to, and (d) apply the reasoning to a fresh task. Passing code tests alone would establish behaviour, not the design decision. Hints and prior examples must be recorded separately from independent evidence. Do not award mastery until the tasks, expected alternatives, fixtures, and rubric are authored and reviewed.

### Required authoring before publication

- Pin a JavaScript runtime and execute every worked example and reference answer.
- Write visible and hidden fixtures, including invalid-return and boundary cases.
- Validate that a simple conditional is accepted when the requirements warrant it; a rubric must not force Strategy everywhere.
- Add misconception-specific feedback and a private solution section that learner retrieval cannot expose.
- Review the lesson's claims and examples with an instructor and record the reviewer and content version.

After this pilot passes review, use the same capability structure for another language while writing idiomatic examples and tests for that language. Do not copy JavaScript function syntax into C, C++, Rust, or Python units.

The first independent exercise and its instructor-only check contract are drafted in [Strategy in JavaScript](curriculum/STRATEGY_JAVASCRIPT_PILOT.md). The existing JSON-only function grader cannot yet pass callback arguments, so this exercise is intentionally outside the learner catalog.
