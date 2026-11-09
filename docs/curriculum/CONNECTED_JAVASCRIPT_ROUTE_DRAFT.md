# Connected JavaScript route: authoring draft

Status: draft for review, 9 November 2026. These tasks are outside the learner catalog and award no progress or mastery.

The route branches after JavaScript conditions and functions. Binary search uses conditionals and a maintained window; Strategy uses passing a function as a value. Binary search is **not** a prerequisite for Strategy. The versioned candidate links are in `data/curriculum/connected-route-pilot.json` and remain advisory.

## Unit A: functions as values

**Capability:** pass a function to another function, predict when it is called, and describe its input and return contract. Existing JavaScript stage 4 teaches calls and returns but does not explicitly teach passing a function as an argument.

**Worked example:**

```javascript
function applyToScore(score, transform) {
  return transform(score);
}
const addTwo = value => value + 2;
applyToScore(5, addTwo); // 7
```

The caller chooses `addTwo`. `applyToScore` receives the function value and calls it exactly once with `5`. It returns the callback's result; it does not print it or choose the transformation itself.

**Guided check:** Ask the learner to predict the result when the caller passes `value => value * 3`, then explain why `applyToScore(5, addTwo())` fails the contract: `addTwo()` is invoked immediately without a score and its numeric result is passed instead of a function.

**Independent task draft:** Implement `applyAdjustment(total, adjustment)` for a nonnegative numeric total. Call the supplied function once with `total`, require a finite nonnegative numeric result, and return it. Do not select an adjustment based on a string name. A later rubric must distinguish a callback contract error from a calculation error and include a fresh domain transfer check. This task is ungraded until fixtures and review are complete.

## Unit B: binary search invariant

**Capability:** given a sorted ascending array and a target, return the index of the first element greater than or equal to the target, or the array length if none exists. Explain why the search window keeps the answer.

Use a half-open window `[lo, hi)`, initially `[0, length)`. The answer is always inside `[lo, hi]` as an insertion boundary. At each step, if `values[mid] < target`, all positions through `mid` are too small, so set `lo = mid + 1`; otherwise keep `mid` by setting `hi = mid`. Stop when `lo === hi`. The loop shrinks on every iteration. This requires sorted input; an unsorted array does not support the elimination argument.

**Worked example:** For `[1, 3, 3, 8]` and target `3`, the result is index `1`. For target `9`, the result is `4`. Check the empty array, a target below the first element, duplicates, and a target above the last element.

**Independent task draft:** Implement `firstAtLeast(values, target)` under the stated sorted-input contract. Explain the invariant and why duplicate values return the first matching position. A fresh transfer task should ask for the first day a monotonic threshold is reached, so a memorized array template alone is insufficient. The verification script checks behavior, not the explanation or transfer reasoning.

## Unit C: Strategy in JavaScript

Use `STRATEGY_JAVASCRIPT_PILOT.md` for the notification-formatting task. Its behavior checker can pass a callback in the configured execution backend. A pass is still only behavior evidence. The design rubric must accept a simple conditional when variation is fixed and local. An independent transfer task and reviewed decision explanation are required before this becomes a graded pathway.

## Review and publication gate

For each unit, record reviewer, version, objective, prerequisite proof, worked-trace check, independent task fixtures, known bad submissions, feedback, and transfer evidence. Run `node tools/verify_connected_route.mjs` for local example and boundary checks. Verify the Strategy callback checker in the production container. Review all learner-facing text for correctness and answer leakage before adding it to `data/content`. Only application assessment policy may turn a reviewed task result into progress; opening this draft cannot.
