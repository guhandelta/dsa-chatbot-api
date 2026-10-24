# CSS3 Debug Exercises

A RAG-training corpus of 300 debugging exercises for CSS3. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: semantics, accessibility, responsive layout, cascade, components, performance, security, and testing

## CSS-E-001: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-002: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-003: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-004: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-005: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-006: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-007: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-008: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-009: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-010: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-011: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-012: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-013: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-014: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-015: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-016: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-017: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-018: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-019: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-020: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-021: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-022: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-023: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-024: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-025: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-026: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-027: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-028: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-029: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-030: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-031: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-032: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-033: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-034: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-035: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-036: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-037: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-038: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-039: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-040: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-041: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-042: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-043: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-044: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-045: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-046: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-047: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-048: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-049: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-050: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-051: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-052: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-053: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-054: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-055: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-056: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-057: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-058: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-059: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-060: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-061: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-062: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-063: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-064: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-065: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-066: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-067: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-068: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-069: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-070: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-071: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-072: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-073: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-074: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-075: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-076: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-077: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-078: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-079: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-080: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-081: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-082: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-083: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-084: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-085: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-086: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-087: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-088: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-089: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-090: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-E-091: specificity conflict

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-E-092: unexpected width

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-E-093: shrinking content

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-E-094: implicit columns

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-E-095: z-index ineffective

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-E-096: desktop overflow

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-E-097: focus removed

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-E-098: motion sickness

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-E-099: hidden content still accessible

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-E-100: invalid fallback

- Difficulty: Easy
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-001: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-002: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-003: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-004: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-005: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-006: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-007: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-008: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-009: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-010: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-011: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-012: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-013: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-014: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-015: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-016: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-017: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-018: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-019: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-020: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-021: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-022: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-023: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-024: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-025: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-026: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-027: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-028: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-029: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-030: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-031: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-032: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-033: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-034: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-035: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-036: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-037: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-038: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-039: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-040: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-041: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-042: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-043: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-044: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-045: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-046: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-047: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-048: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-049: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-050: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-051: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-052: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-053: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-054: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-055: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-056: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-057: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-058: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-059: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-060: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-061: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-062: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-063: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-064: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-065: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-066: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-067: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-068: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-069: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-070: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-071: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-072: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-073: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-074: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-075: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-076: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-077: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-078: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-079: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-080: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-081: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-082: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-083: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-084: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-085: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-086: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-087: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-088: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-089: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-090: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-M-091: specificity conflict

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-M-092: unexpected width

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-M-093: shrinking content

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-M-094: implicit columns

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-M-095: z-index ineffective

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-M-096: desktop overflow

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-M-097: focus removed

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-M-098: motion sickness

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-M-099: hidden content still accessible

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-M-100: invalid fallback

- Difficulty: Medium
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-001: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-002: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-003: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-004: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-005: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-006: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-007: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-008: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-009: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-010: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-011: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-012: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-013: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-014: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-015: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-016: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-017: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-018: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-019: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-020: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-021: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-022: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-023: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-024: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-025: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-026: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-027: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-028: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-029: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-030: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-031: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-032: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-033: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-034: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-035: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-036: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-037: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-038: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-039: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-040: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-041: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-042: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-043: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-044: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-045: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-046: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-047: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-048: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-049: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-050: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-051: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-052: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-053: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-054: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-055: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-056: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-057: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-058: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-059: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-060: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-061: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-062: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-063: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-064: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-065: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-066: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-067: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-068: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-069: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-070: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-071: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-072: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-073: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-074: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-075: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-076: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-077: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-078: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-079: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-080: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-081: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-082: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-083: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-084: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-085: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-086: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-087: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-088: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-089: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-090: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```

## CSS-H-091: specificity conflict

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Cascade
- Concept: specificity conflict
- Symptom: The intended color is ignored.
- Diagnostic goal: Inspect specificity and source order before adding !important.

### Buggy code

```css
.card .title { color: blue; }
.title { color: red; }
```

### Expected diagnosis

The compound selector has greater specificity than the later class selector.

### Corrected code

```css
.card .title { color: red; }
```

### Regression tests

```css
assert computed color is red
```

## CSS-H-092: unexpected width

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Box model
- Concept: unexpected width
- Symptom: A 100% input overflows its container.
- Diagnostic goal: Account for padding and borders in sizing.

### Buggy code

```css
input { width: 100%; padding: 1rem; }
```

### Expected diagnosis

content-box adds padding to the declared width.

### Corrected code

```css
*, *::before, *::after { box-sizing: border-box; }
input { width: 100%; padding: 1rem; }
```

### Regression tests

```css
assert input bounding box fits container
```

## CSS-H-093: shrinking content

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Flexbox
- Concept: shrinking content
- Symptom: A label is clipped beside a flexible panel.
- Diagnostic goal: Set the intended min-width and growth behavior.

### Buggy code

```css
.row { display:flex; }
.label { width: 240px; }
.panel { flex: 1; }
```

### Expected diagnosis

Flex items default to min-width:auto and may refuse to shrink or force overflow.

### Corrected code

```css
.panel { flex: 1 1 auto; min-width: 0; }
```

### Regression tests

```css
assert long text remains within the row
```

## CSS-H-094: implicit columns

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Grid
- Concept: implicit columns
- Symptom: Cards have inconsistent widths.
- Diagnostic goal: Declare the grid tracks and responsive breakpoint explicitly.

### Buggy code

```css
.cards { display:grid; grid-template-columns: 1fr 1fr; }
```

### Expected diagnosis

Fixed tracks do not adapt to the available width.

### Corrected code

```css
.cards { display:grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
```

### Regression tests

```css
assert one column on narrow and multiple on wide viewport
```

## CSS-H-095: z-index ineffective

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Positioning
- Concept: z-index ineffective
- Symptom: A modal appears behind content.
- Diagnostic goal: Give positioned elements a deliberate stacking context and z-index.

### Buggy code

```css
.modal { z-index: 1000; }
```

### Expected diagnosis

z-index does not apply to a static element and ancestor stacking contexts can constrain it.

### Corrected code

```css
.modal { position: fixed; inset: 0; z-index: 1000; }
```

### Regression tests

```css
assert modal paints above page content
```

## CSS-H-096: desktop overflow

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Responsive
- Concept: desktop overflow
- Symptom: The page scrolls horizontally on phones.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Find fixed widths and allow content to wrap or shrink.
```

### Expected diagnosis

.container { width: 1200px; }

### Corrected code

```css
.container { width: min(100% - 2rem, 1200px); margin-inline:auto; }
```

### Regression tests

```css
assert no horizontal overflow at 320px
```

## CSS-H-097: focus removed

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Accessibility
- Concept: focus removed
- Symptom: Keyboard users cannot see focus.
- Diagnostic goal: Preserve a visible focus indicator.

### Buggy code

```css
button:focus { outline: none; }
```

### Expected diagnosis

Removing the outline without replacement makes keyboard position invisible.

### Corrected code

```css
button:focus-visible { outline: 3px solid currentColor; outline-offset: 3px; }
```

### Regression tests

```css
assert focus-visible has nonzero outline
```

## CSS-H-098: motion sickness

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Animation
- Concept: motion sickness
- Symptom: The interface animates for users who request reduced motion.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
Respect the user media preference.
```

### Expected diagnosis

.panel { transition: transform .4s; }

### Corrected code

```css
.panel { transition: transform .4s; }
@media (prefers-reduced-motion: reduce) { .panel { transition: none; } }
```

### Regression tests

```css
assert reduced-motion disables transition
```

## CSS-H-099: hidden content still accessible

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Selectors
- Concept: hidden content still accessible
- Symptom: An element is visually hidden but remains in the focus order.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.visually-hidden { opacity: 0; }
```

### Expected diagnosis

Opacity hides pixels but does not remove the element from interaction or accessibility flow.

### Corrected code

```css
.visually-hidden { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

### Regression tests

```css
assert decorative element is not focusable
```

## CSS-H-100: invalid fallback

- Difficulty: Hard
- Language/framework: CSS3
- Perspective: Custom properties
- Concept: invalid fallback
- Symptom: A component loses its background color.
- Diagnostic goal: Check the boundary contract before styling around the symptom.

### Buggy code

```css
.card { background: var(--card-color); }
```

### Expected diagnosis

An undefined custom property makes the whole declaration invalid.

### Corrected code

```css
.card { background: var(--card-color, white); }
```

### Regression tests

```css
assert computed background is white when variable absent
```
