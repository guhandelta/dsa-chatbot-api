# HTML5 Debug Exercises

A RAG-training corpus of 300 debugging exercises for HTML5. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: semantics, accessibility, responsive layout, cascade, components, performance, security, and testing

## HTML-E-001: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-002: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-003: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-004: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-005: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-006: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-007: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-008: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-009: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-010: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-011: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-012: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-013: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-014: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-015: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-016: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-017: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-018: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-019: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-020: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-021: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-022: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-023: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-024: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-025: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-026: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-027: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-028: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-029: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-030: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-031: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-032: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-033: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-034: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-035: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-036: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-037: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-038: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-039: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-040: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-041: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-042: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-043: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-044: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-045: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-046: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-047: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-048: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-049: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-050: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-051: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-052: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-053: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-054: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-055: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-056: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-057: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-058: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-059: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-060: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-061: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-062: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-063: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-064: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-065: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-066: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-067: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-068: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-069: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-070: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-071: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-072: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-073: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-074: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-075: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-076: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-077: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-078: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-079: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-080: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-081: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-082: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-083: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-084: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-085: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-086: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-087: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-088: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-089: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-090: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-E-091: heading hierarchy

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-E-092: missing label

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-E-093: wrong input type

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-E-094: image alternative

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-E-095: button used for navigation

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-E-096: layout table

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-E-097: missing viewport

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-E-098: unsafe target blank

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-E-099: video inaccessible

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-E-100: unoptimized image

- Difficulty: Easy
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-001: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-002: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-003: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-004: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-005: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-006: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-007: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-008: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-009: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-010: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-011: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-012: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-013: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-014: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-015: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-016: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-017: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-018: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-019: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-020: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-021: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-022: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-023: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-024: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-025: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-026: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-027: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-028: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-029: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-030: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-031: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-032: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-033: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-034: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-035: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-036: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-037: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-038: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-039: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-040: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-041: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-042: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-043: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-044: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-045: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-046: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-047: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-048: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-049: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-050: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-051: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-052: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-053: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-054: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-055: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-056: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-057: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-058: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-059: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-060: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-061: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-062: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-063: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-064: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-065: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-066: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-067: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-068: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-069: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-070: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-071: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-072: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-073: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-074: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-075: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-076: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-077: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-078: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-079: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-080: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-081: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-082: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-083: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-084: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-085: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-086: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-087: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-088: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-089: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-090: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-M-091: heading hierarchy

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-M-092: missing label

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-M-093: wrong input type

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-M-094: image alternative

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-M-095: button used for navigation

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-M-096: layout table

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-M-097: missing viewport

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-M-098: unsafe target blank

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-M-099: video inaccessible

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-M-100: unoptimized image

- Difficulty: Medium
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-001: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-002: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-003: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-004: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-005: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-006: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-007: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-008: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-009: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-010: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-011: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-012: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-013: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-014: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-015: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-016: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-017: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-018: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-019: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-020: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-021: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-022: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-023: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-024: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-025: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-026: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-027: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-028: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-029: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-030: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-031: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-032: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-033: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-034: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-035: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-036: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-037: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-038: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-039: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-040: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-041: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-042: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-043: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-044: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-045: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-046: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-047: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-048: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-049: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-050: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-051: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-052: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-053: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-054: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-055: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-056: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-057: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-058: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-059: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-060: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-061: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-062: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-063: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-064: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-065: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-066: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-067: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-068: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-069: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-070: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-071: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-072: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-073: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-074: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-075: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-076: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-077: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-078: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-079: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-080: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-081: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-082: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-083: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-084: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-085: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-086: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-087: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-088: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-089: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-090: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```

## HTML-H-091: heading hierarchy

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Semantics
- Concept: heading hierarchy
- Symptom: Screen-reader users cannot understand page structure.
- Diagnostic goal: Use headings to express document hierarchy, not visual size.

### Buggy code

```html
<div class="h1">Products</div>
<h4>Featured</h4>
```

### Expected diagnosis

A styled div is not a heading and h4 skips the logical level.

### Corrected code

```html
<h1>Products</h1>
<h2>Featured</h2>
```

### Regression tests

```html
assert accessibility tree exposes h1 followed by h2
```

## HTML-H-092: missing label

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: missing label
- Symptom: Clicking a field label does not focus the input.
- Diagnostic goal: Associate a visible label with a control.

### Buggy code

```html
<label>Email</label>
<input type="email" name="email">
```

### Expected diagnosis

A label without for and a matching id has no programmatic association.

### Corrected code

```html
<label for="email">Email</label>
<input id="email" type="email" name="email">
```

### Regression tests

```html
assert label click focuses #email
```

## HTML-H-093: wrong input type

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Forms
- Concept: wrong input type
- Symptom: Mobile users get a poor keyboard and weak validation.
- Diagnostic goal: Use the input type matching the value contract.

### Buggy code

```html
<input type="text" name="email">
```

### Expected diagnosis

Text does not communicate email semantics or enable native email validation.

### Corrected code

```html
<input type="email" name="email" autocomplete="email" required>
```

### Regression tests

```html
assert invalid email blocks submission
```

## HTML-H-094: image alternative

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Accessibility
- Concept: image alternative
- Symptom: Important content is missing for nonvisual users.
- Diagnostic goal: Provide concise alt text or mark decorative images empty.

### Buggy code

```html
<img src="chart.png">
```

### Expected diagnosis

Without alt, the image has no accessible name and screen readers may announce its filename.

### Corrected code

```html
<img src="chart.png" alt="Sales increased 24 percent in Q4">
```

### Regression tests

```html
assert accessible name describes the chart
```

## HTML-H-095: button used for navigation

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Links
- Concept: button used for navigation
- Symptom: Keyboard behavior and browser semantics are inconsistent.
- Diagnostic goal: Use an anchor for navigation and a button for actions.

### Buggy code

```html
<button onclick="location.href='/help'">Help</button>
```

### Expected diagnosis

A navigation target should be a link with URL semantics, history, and open-in-new-tab behavior.

### Corrected code

```html
<a href="/help">Help</a>
```

### Regression tests

```html
assert keyboard activation and href navigation work
```

## HTML-H-096: layout table

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Tables
- Concept: layout table
- Symptom: Screen readers announce decorative cells as data.
- Diagnostic goal: Use CSS layout for layout and table semantics for tabular data.

### Buggy code

```html
<table><tr><td><nav>Menu</nav></td></tr></table>
```

### Expected diagnosis

A layout table creates a misleading data structure.

### Corrected code

```html
<div class="layout"><nav>Menu</nav></div>
```

### Regression tests

```html
assert accessibility tree has no table for layout
```

## HTML-H-097: missing viewport

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Metadata
- Concept: missing viewport
- Symptom: The mobile page renders zoomed out.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Expected diagnosis

Mobile browsers use a desktop layout viewport without the viewport declaration.

### Corrected code

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### Regression tests

```html
assert mobile viewport width equals device width
```

## HTML-H-098: unsafe target blank

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Security
- Concept: unsafe target blank
- Symptom: A new tab can access the opener.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<a href="https://example.com" target="_blank">Docs</a>
```

### Expected diagnosis

A new browsing context may retain window.opener access.

### Corrected code

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">Docs</a>
```

### Regression tests

```html
assert opener is null in the new tab
```

## HTML-H-099: video inaccessible

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Media
- Concept: video inaccessible
- Symptom: Users cannot follow spoken content.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<video controls src="lesson.mp4"></video>
```

### Expected diagnosis

The video has no captions track for deaf or hard-of-hearing users.

### Corrected code

```html
<video controls src="lesson.mp4"><track kind="captions" src="lesson.en.vtt" srclang="en" label="English"></video>
```

### Regression tests

```html
assert captions track is available
```

## HTML-H-100: unoptimized image

- Difficulty: Hard
- Language/framework: HTML5
- Perspective: Performance
- Concept: unoptimized image
- Symptom: Largest contentful paint is slow.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```html
<img src="hero.jpg">
```

### Expected diagnosis

The browser downloads an unnecessarily large image and lacks responsive hints.

### Corrected code

```html
<img src="hero.jpg" srcset="hero-480.jpg 480w, hero-1200.jpg 1200w" sizes="100vw" loading="eager" alt="">
```

### Regression tests

```html
assert mobile selects the smaller candidate
```
