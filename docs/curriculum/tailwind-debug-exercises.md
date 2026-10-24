# Tailwind Debug Exercises

A RAG-training corpus of 300 debugging exercises for Tailwind. Corrected code is editorial training material and must be stripped from learner-facing challenge responses.

## Coverage

- Easy: 100 exercises
- Medium: 100 exercises
- Hard: 100 exercises
- Perspectives: semantics, accessibility, responsive layout, cascade, components, performance, security, and testing

## TW-E-001: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-002: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-003: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-004: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-005: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-006: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-007: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-008: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-009: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-010: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-011: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-012: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-013: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-014: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-015: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-016: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-017: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-018: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-019: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-020: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-021: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-022: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-023: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-024: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-025: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-026: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-027: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-028: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-029: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-030: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-031: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-032: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-033: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-034: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-035: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-036: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-037: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-038: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-039: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-040: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-041: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-042: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-043: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-044: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-045: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-046: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-047: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-048: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-049: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-050: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-051: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-052: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-053: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-054: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-055: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-056: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-057: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-058: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-059: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-060: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-061: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-062: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-063: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-064: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-065: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-066: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-067: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-068: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-069: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-070: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-071: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-072: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-073: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-074: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-075: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-076: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-077: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-078: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-079: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-080: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-081: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-082: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-083: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-084: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-085: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-086: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-087: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-088: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-089: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-090: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-E-091: dynamic class missing

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-E-092: mobile-first misunderstanding

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-E-093: wrong axis utility

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-E-094: flex child overflow

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-E-095: stacking context surprise

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-E-096: hover-only action inaccessible

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-E-097: variant not configured

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-E-098: text clipped

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-E-099: arbitrary value typo

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-E-100: focus ring removed

- Difficulty: Easy
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-001: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-002: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-003: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-004: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-005: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-006: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-007: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-008: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-009: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-010: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-011: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-012: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-013: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-014: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-015: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-016: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-017: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-018: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-019: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-020: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-021: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-022: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-023: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-024: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-025: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-026: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-027: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-028: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-029: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-030: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-031: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-032: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-033: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-034: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-035: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-036: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-037: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-038: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-039: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-040: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-041: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-042: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-043: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-044: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-045: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-046: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-047: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-048: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-049: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-050: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-051: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-052: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-053: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-054: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-055: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-056: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-057: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-058: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-059: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-060: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-061: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-062: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-063: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-064: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-065: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-066: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-067: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-068: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-069: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-070: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-071: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-072: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-073: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-074: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-075: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-076: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-077: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-078: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-079: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-080: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-081: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-082: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-083: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-084: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-085: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-086: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-087: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-088: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-089: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-090: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-M-091: dynamic class missing

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-M-092: mobile-first misunderstanding

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-M-093: wrong axis utility

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-M-094: flex child overflow

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-M-095: stacking context surprise

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-M-096: hover-only action inaccessible

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-M-097: variant not configured

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-M-098: text clipped

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-M-099: arbitrary value typo

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-M-100: focus ring removed

- Difficulty: Medium
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-001: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-002: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-003: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-004: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-005: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-006: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-007: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-008: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-009: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-010: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-011: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-012: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-013: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-014: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-015: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-016: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-017: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-018: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-019: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-020: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-021: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-022: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-023: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-024: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-025: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-026: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-027: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-028: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-029: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-030: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-031: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-032: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-033: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-034: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-035: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-036: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-037: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-038: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-039: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-040: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-041: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-042: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-043: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-044: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-045: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-046: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-047: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-048: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-049: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-050: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-051: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-052: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-053: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-054: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-055: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-056: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-057: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-058: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-059: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-060: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-061: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-062: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-063: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-064: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-065: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-066: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-067: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-068: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-069: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-070: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-071: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-072: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-073: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-074: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-075: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-076: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-077: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-078: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-079: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-080: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-081: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-082: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-083: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-084: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-085: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-086: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-087: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-088: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-089: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-090: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```

## TW-H-091: dynamic class missing

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Content scanning
- Concept: dynamic class missing
- Symptom: A runtime-selected color has no styles in production.
- Diagnostic goal: Use complete static class names or safelist generated variants.

### Buggy code

```html
<div className={`bg-${color}-500`}>Status</div>
```

### Expected diagnosis

Tailwind scans class tokens statically and cannot infer arbitrary runtime interpolation.

### Corrected code

```html
<div className={color === "red" ? "bg-red-500" : "bg-green-500"}>Status</div>
```

### Regression tests

```html
assert production CSS contains both background utilities
```

## TW-H-092: mobile-first misunderstanding

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Responsive
- Concept: mobile-first misunderstanding
- Symptom: The desktop style appears on small screens.
- Diagnostic goal: Apply the base class to mobile and add breakpoint overrides.

### Buggy code

```html
<div class="md:hidden block">Menu</div>
```

### Expected diagnosis

The base block wins below md; the intended mobile visibility must be explicit and breakpoint order understood.

### Corrected code

```html
<div class="block md:hidden">Menu</div>
```

### Regression tests

```html
assert visible on mobile and hidden at md
```

## TW-H-093: wrong axis utility

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Spacing
- Concept: wrong axis utility
- Symptom: Only horizontal padding changes.
- Diagnostic goal: Choose p, px, py, or directional utilities accurately.

### Buggy code

```html
<section class="px-6">Content</section>
```

### Expected diagnosis

px applies left and right padding, not vertical spacing.

### Corrected code

```html
<section class="py-6">Content</section>
```

### Regression tests

```html
assert top and bottom padding equal 1.5rem
```

## TW-H-094: flex child overflow

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Layout
- Concept: flex child overflow
- Symptom: Long content forces horizontal scrolling.
- Diagnostic goal: Allow flex children to shrink below intrinsic width.

### Buggy code

```html
<div class="flex"><aside class="w-64">...</aside><main class="flex-1">long</main></div>
```

### Expected diagnosis

flex-1 alone can retain an automatic minimum width.

### Corrected code

```html
<main class="min-w-0 flex-1">long</main>
```

### Regression tests

```html
assert main content does not overflow the flex row
```

## TW-H-095: stacking context surprise

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Z-index
- Concept: stacking context surprise
- Symptom: A high z-index tooltip remains behind a panel.
- Diagnostic goal: Inspect ancestor stacking contexts and position requirements.

### Buggy code

```html
<div class="z-50">Tooltip</div>
```

### Expected diagnosis

z-index applies meaningfully to positioned elements and cannot escape an ancestor stacking context.

### Corrected code

```html
<div class="relative z-50">Tooltip</div>
```

### Regression tests

```html
assert tooltip paints above the panel
```

## TW-H-096: hover-only action inaccessible

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: States
- Concept: hover-only action inaccessible
- Symptom: Keyboard users cannot reach the visible action state.
- Diagnostic goal: Pair hover styles with focus-visible styles.

### Buggy code

```html
<button class="opacity-0 group-hover:opacity-100">Delete</button>
```

### Expected diagnosis

Only mouse hover changes opacity; keyboard focus leaves the button invisible.

### Corrected code

```html
<button class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100">Delete</button>
```

### Regression tests

```html
assert focus-visible action has opacity 1
```

## TW-H-097: variant not configured

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Dark mode
- Concept: variant not configured
- Symptom: Dark classes never apply.
- Diagnostic goal: Align class strategy and root dark marker with configuration.

### Buggy code

```html
<div class="dark:bg-gray-900">...</div>
```

### Expected diagnosis

The project may use media strategy while expecting a class strategy, or lack the dark marker.

### Corrected code

```html
<html class="dark"><div class="dark:bg-gray-900">...</div></html>
```

### Regression tests

```html
assert dark root produces dark background
```

## TW-H-098: text clipped

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Typography
- Concept: text clipped
- Symptom: A heading overflows its card.
- Diagnostic goal: Use wrapping or truncation intentionally.

### Buggy code

```html
<h2 class="whitespace-nowrap">Very long title...</h2>
```

### Expected diagnosis

nowrap prevents wrapping and can exceed the container.

### Corrected code

```html
<h2 class="break-words">Very long title...</h2>
```

### Regression tests

```html
assert long title remains within card
```

## TW-H-099: arbitrary value typo

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Build
- Concept: arbitrary value typo
- Symptom: A custom width is ignored.
- Diagnostic goal: Use valid arbitrary-value syntax and inspect generated CSS.

### Buggy code

```html
<div class="w-[calc(100%-2rem]">...</div>
```

### Expected diagnosis

The arbitrary value has unbalanced brackets and is discarded.

### Corrected code

```html
<div class="w-[calc(100%-2rem)]">...</div>
```

### Regression tests

```html
assert computed width equals container minus 2rem
```

## TW-H-100: focus ring removed

- Difficulty: Hard
- Language/framework: Tailwind
- Perspective: Accessibility
- Concept: focus ring removed
- Symptom: Keyboard focus is invisible.
- Diagnostic goal: Keep a visible focus treatment in utility composition.

### Buggy code

```html
<button class="focus:outline-none">Save</button>
```

### Expected diagnosis

Removing the browser outline without a replacement harms keyboard navigation.

### Corrected code

```html
<button class="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">Save</button>
```

### Regression tests

```html
assert focus-visible ring is present
```
