# Bootstrap 5 Debug Exercises

A RAG-training corpus of 300 debugging exercises for Bootstrap 5. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: semantics, accessibility, responsive layout, cascade, components, performance, security, and testing

## BOOT-E-001: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-002: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-003: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-004: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-005: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-006: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-007: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-008: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-009: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-010: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-011: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-012: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-013: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-014: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-015: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-016: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-017: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-018: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-019: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-020: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-021: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-022: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-023: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-024: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-025: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-026: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-027: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-028: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-029: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-030: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-031: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-032: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-033: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-034: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-035: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-036: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-037: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-038: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-039: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-040: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-041: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-042: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-043: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-044: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-045: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-046: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-047: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-048: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-049: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-050: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-051: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-052: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-053: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-054: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-055: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-056: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-057: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-058: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-059: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-060: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-061: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-062: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-063: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-064: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-065: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-066: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-067: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-068: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-069: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-070: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-071: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-072: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-073: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-074: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-075: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-076: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-077: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-078: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-079: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-080: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-081: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-082: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-083: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-084: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-085: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-086: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-087: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-088: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-089: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-090: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-E-091: container breakpoint mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-E-092: utility direction typo

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-E-093: collapse not initialized

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-E-094: invalid feedback hidden

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-E-095: modal missing label

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-E-096: d-none conflict

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-E-097: alignment utility mismatch

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-E-098: responsive wrapper missing

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-E-099: text contrast failure

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-E-100: v4 class on v5

- Difficulty: Easy
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-001: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-002: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-003: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-004: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-005: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-006: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-007: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-008: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-009: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-010: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-011: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-012: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-013: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-014: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-015: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-016: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-017: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-018: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-019: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-020: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-021: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-022: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-023: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-024: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-025: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-026: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-027: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-028: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-029: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-030: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-031: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-032: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-033: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-034: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-035: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-036: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-037: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-038: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-039: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-040: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-041: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-042: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-043: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-044: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-045: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-046: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-047: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-048: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-049: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-050: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-051: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-052: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-053: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-054: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-055: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-056: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-057: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-058: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-059: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-060: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-061: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-062: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-063: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-064: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-065: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-066: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-067: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-068: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-069: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-070: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-071: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-072: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-073: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-074: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-075: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-076: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-077: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-078: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-079: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-080: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-081: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-082: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-083: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-084: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-085: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-086: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-087: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-088: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-089: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-090: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-M-091: container breakpoint mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-M-092: utility direction typo

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-M-093: collapse not initialized

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-M-094: invalid feedback hidden

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-M-095: modal missing label

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-M-096: d-none conflict

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-M-097: alignment utility mismatch

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-M-098: responsive wrapper missing

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-M-099: text contrast failure

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-M-100: v4 class on v5

- Difficulty: Medium
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-001: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-002: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-003: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-004: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-005: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-006: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-007: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-008: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-009: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-010: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-011: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-012: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-013: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-014: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-015: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-016: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-017: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-018: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-019: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-020: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-021: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-022: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-023: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-024: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-025: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-026: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-027: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-028: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-029: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-030: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-031: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-032: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-033: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-034: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-035: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-036: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-037: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-038: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-039: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-040: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-041: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-042: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-043: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-044: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-045: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-046: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-047: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-048: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-049: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-050: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-051: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-052: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-053: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-054: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-055: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-056: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-057: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-058: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-059: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-060: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-061: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-062: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-063: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-064: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-065: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-066: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-067: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-068: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-069: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-070: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-071: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-072: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-073: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-074: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-075: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-076: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-077: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-078: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-079: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-080: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-081: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-082: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-083: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-084: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-085: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-086: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-087: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-088: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-089: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-090: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```

## BOOT-H-091: container breakpoint mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Grid
- Concept: container breakpoint mismatch
- Symptom: Columns stack at an unexpected width.
- Diagnostic goal: Match column classes to the intended responsive breakpoint.

### Buggy code

```html
<div class="col-md-6 col-lg-6">Card</div>
```

### Expected diagnosis

The md breakpoint keeps two columns only at medium widths; the design may require sm or xl behavior.

### Corrected code

```html
<div class="col-12 col-sm-6 col-lg-6">Card</div>
```

### Regression tests

```html
assert one column below sm and two above sm
```

## BOOT-H-092: utility direction typo

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Spacing
- Concept: utility direction typo
- Symptom: The margin is applied on the wrong axis.
- Diagnostic goal: Use Bootstrap’s directional utility vocabulary precisely.

### Buggy code

```html
<div class="ms-4">Content</div>
```

### Expected diagnosis

ms means margin-start, not vertical spacing.

### Corrected code

```html
<div class="my-4">Content</div>
```

### Regression tests

```html
assert top and bottom margins are applied
```

## BOOT-H-093: collapse not initialized

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Components
- Concept: collapse not initialized
- Symptom: The navbar toggle does nothing.
- Diagnostic goal: Load the Bootstrap JavaScript bundle and matching data attributes.

### Buggy code

```html
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Expected diagnosis

The component needs bootstrap.bundle.js for the collapse behavior and a matching target id.

### Corrected code

```html
<script src="bootstrap.bundle.min.js"></script>
<button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#nav">Menu</button>
```

### Regression tests

```html
assert click toggles #nav.show
```

## BOOT-H-094: invalid feedback hidden

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Forms
- Concept: invalid feedback hidden
- Symptom: The error message never appears.
- Diagnostic goal: Use the validation state class and required structure.

### Buggy code

```html
<input class="form-control"><div class="invalid-feedback">Required</div>
```

### Expected diagnosis

Bootstrap displays invalid-feedback when the control or form has the invalid state.

### Corrected code

```html
<input class="form-control is-invalid"><div class="invalid-feedback">Required</div>
```

### Regression tests

```html
assert invalid feedback is visible
```

## BOOT-H-095: modal missing label

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Accessibility
- Concept: modal missing label
- Symptom: A modal opens without an accessible name.
- Diagnostic goal: Set modal title association and dialog semantics.

### Buggy code

```html
<div class="modal" id="dialog"><div class="modal-dialog">...</div></div>
```

### Expected diagnosis

The dialog has no labelledby relationship for assistive technology.

### Corrected code

```html
<div class="modal" id="dialog" aria-labelledby="dialogTitle"><div class="modal-dialog"><h2 id="dialogTitle">Details</h2></div></div>
```

### Regression tests

```html
assert dialog accessible name is Details
```

## BOOT-H-096: d-none conflict

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Display
- Concept: d-none conflict
- Symptom: Responsive content never appears.
- Diagnostic goal: Order display utilities from the desired breakpoint.

### Buggy code

```html
<div class="d-none d-md-none d-lg-block">Desktop</div>
```

### Expected diagnosis

The second d-md-none keeps the element hidden through md; inspect utility order and breakpoint intent.

### Corrected code

```html
<div class="d-none d-lg-block">Desktop</div>
```

### Regression tests

```html
assert hidden below lg and visible at lg
```

## BOOT-H-097: alignment utility mismatch

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Flex
- Concept: alignment utility mismatch
- Symptom: Items are centered on the wrong axis.
- Diagnostic goal: Distinguish justify-content from align-items.

### Buggy code

```html
<div class="d-flex align-items-center">...</div>
```

### Expected diagnosis

align-items controls the cross axis; horizontal centering in a row uses justify-content-center.

### Corrected code

```html
<div class="d-flex justify-content-center">...</div>
```

### Regression tests

```html
assert items center horizontally
```

## BOOT-H-098: responsive wrapper missing

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Tables
- Concept: responsive wrapper missing
- Symptom: A table breaks the viewport on phones.
- Diagnostic goal: Wrap wide tabular content in the responsive utility.

### Buggy code

```html
<table class="table">...</table>
```

### Expected diagnosis

The table itself does not create horizontal scrolling.

### Corrected code

```html
<div class="table-responsive"><table class="table">...</table></div>
```

### Regression tests

```html
assert wrapper scrolls horizontally without page overflow
```

## BOOT-H-099: text contrast failure

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Utilities
- Concept: text contrast failure
- Symptom: Muted text is unreadable on a dark background.
- Diagnostic goal: Choose a contextual text color with sufficient contrast.

### Buggy code

```html
<div class="bg-dark text-muted">Status</div>
```

### Expected diagnosis

text-muted can have insufficient contrast against bg-dark.

### Corrected code

```html
<div class="bg-dark text-light">Status</div>
```

### Regression tests

```html
assert contrast ratio meets WCAG target
```

## BOOT-H-100: v4 class on v5

- Difficulty: Hard
- Language/framework: Bootstrap 5
- Perspective: Versioning
- Concept: v4 class on v5
- Symptom: A spacing or float utility has no effect.
- Diagnostic goal: Check the Bootstrap major-version utility names.

### Buggy code

```html
<div class="float-right mr-3">...</div>
```

### Expected diagnosis

Bootstrap 5 uses float-end and me-3 instead of v4 right/mr classes.

### Corrected code

```html
<div class="float-end me-3">...</div>
```

### Regression tests

```html
assert computed float and margin are applied
```
